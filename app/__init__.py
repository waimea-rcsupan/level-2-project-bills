from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY", "dev-secure-bill-budget-token-12345")

@app.get("/")
def show_bills():
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created, price, due_date
            FROM bill
            ORDER BY pinned DESC, created DESC
        """
        params = ()
        raw_bills = db.execute(sql, params).fetchall()
        
        budget_limit = float(session.get('budget_limit', 1000.00))
        bills = []
        total_bills_cost = 0.0
        
        for b in raw_bills:
            bill_dict = dict(b)
            price_val = bill_dict.get('price') if bill_dict.get('price') is not None else 0.00
            total_bills_cost += price_val
            
            bill_dict['display_price'] = f"{price_val:.2f}"
            bills.append(bill_dict)

        remaining_budget = budget_limit - total_bills_cost

        return render_template(
            "pages/bill_list.jinja", 
            bills=bills, 
            total_balance=f"{total_bills_cost:.2f}",
            budget_limit=f"{budget_limit:.2f}",
            remaining_budget=f"{remaining_budget:.2f}"
        )
    
@app.route("/bill/add", methods=["GET", "POST"])
def add_bill():
    if request.method == "POST":
        title = html.escape(request.form.get("title", "").strip())
        body = html.escape(request.form.get("body", "").strip())
        due_date = request.form.get("due_date", "").strip()
        
        try:
            price = float(request.form.get("price", 0.0))
        except ValueError:
            price = 0.0

        pinned = 1 if request.form.get("pinned") else 0
        
        if not title:
            flash("Title is required!", "error")
            return redirect("/bill/add")

        with connect_db() as db:
            sql = "INSERT INTO bill (title, body, pinned, price, due_date) VALUES (?, ?, ?, ?, ?)"
            db.execute(sql, (title, body, pinned, price, due_date))
            db.commit()
            
        flash("Bill added successfully!", "success")
        return redirect("/")
        
    return render_template("pages/bill_form.jinja", bill=None)

@app.route("/bill/edit/<int:bill_id>", methods=["GET", "POST"])
def edit_bill(bill_id):
    with connect_db() as db:
        if request.method == "POST":
            title = html.escape(request.form.get("title", "").strip())
            body = html.escape(request.form.get("body", "").strip())
            due_date = request.form.get("due_date", "").strip()
            pinned = 1 if request.form.get("pinned") else 0
            
            try:
                price = float(request.form.get("price", 0.0))
            except ValueError:
                price = 0.0
            
            if not title:
                flash("Title is required!", "error")
                return redirect(f"/bill/edit/{bill_id}")

            sql = "UPDATE bill SET title = ?, body = ?, pinned = ?, price = ?, due_date = ? WHERE id = ?"
            db.execute(sql, (title, body, pinned, price, due_date, bill_id))
            db.commit()
            
            flash("Bill updated successfully!", "success")
            return redirect("/")
            
        sql = "SELECT id, title, body, pinned, price, due_date FROM bill WHERE id = ?"
        bill = db.execute(sql, (bill_id,)).fetchone()
        
        if not bill:
            flash("Bill not found!", "error")
            return redirect("/")
            
        return render_template("pages/bill_form.jinja", bill=bill)

@app.post("/bill/delete/<int:bill_id>")
def delete_bill(bill_id):
    with connect_db() as db:
        sql = "DELETE FROM bill WHERE id = ?"
        db.execute(sql, (bill_id,))
        db.commit()
        
    flash("Bill deleted successfully!", "success")
    return redirect("/")

@app.post("/bill/balance/<int:bill_id>")
def edit_balance(bill_id):  
    try:
        price = float(request.form.get("price", 0.0))
    except ValueError:
        price = 0.0

    with connect_db() as db:
        sql = "UPDATE bill SET price = ? WHERE id = ?"
        db.execute(sql, (price, bill_id))
        db.commit()

    flash("Balance updated successfully!", "success")
    return redirect("/")

@app.post("/budget/update")
def update_budget_limit():
    try:
        new_limit = float(request.form.get("budget_limit", 0.0))
        session['budget_limit'] = new_limit
        flash("Budget limit updated successfully!", "success")
    except ValueError:
        flash("Please enter a valid numeric format.", "error")
        
    return redirect("/")

load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)