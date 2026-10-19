#===========================================================
# PROJECT NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Home
#-----------------------------------------------------------
@app.get("/")
def show_bills():
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created, price
            FROM bill
            ORDER BY pinned DESC, created DESC
        """
        params = ()
        raw_bills = db.execute(sql, params).fetchall()
        
     
        bills = []
        for b in raw_bills:
            bill_dict = dict(b)
            
            price_val = bill_dict.get('price') if bill_dict.get('price') is not None else 0.00
            bill_dict['display_price'] = f"{price_val:.2f}"
            bills.append(bill_dict)

        return render_template("pages/bill_list.jinja", bills=bills)
    
#-----------------------------------------------------------
# Add a new Bill - Add new Bills
#-----------------------------------------------------------
@app.route("/bill/add", methods=["GET", "POST"])
def add_bill():
    if request.method == "POST":
        title = html.escape(request.form.get("title", "").strip())
        body = html.escape(request.form.get("body", "").strip())
        
        try:
            price = float(request.form.get("price", 0.0))
        except ValueError:
            price = 0.0

        pinned = 1 if request.form.get("pinned") else 0
        
        if not title:
            flash("Title is required!", "error")
            return redirect("/bill/add")

        with connect_db() as db:

            sql = "INSERT INTO bill (title, body, pinned, price) VALUES (?, ?, ?, ?)"
            db.execute(sql, (title, body, pinned, price))
            db.commit()
            
        flash("Bill added successfully!", "success")
        return redirect("/")
        
    return render_template("pages/bill_form.jinja", bill=None)

#-----------------------------------------------------------
# Edit an existing Bill - Modify structural amounts
#-----------------------------------------------------------
@app.route("/bill/edit/<int:bill_id>", methods=["GET", "POST"])
def edit_bill(bill_id):
    with connect_db() as db:
        if request.method == "POST":
            title = html.escape(request.form.get("title", "").strip())
            body = html.escape(request.form.get("body", "").strip())
            pinned = 1 if request.form.get("pinned") else 0
            
            try:
                price = float(request.form.get("price", 0.0))
            except ValueError:
                price = 0.0
            
            if not title:
                flash("Title is required!", "error")
                return redirect(f"/bill/edit/{bill_id}")

            
            sql = "UPDATE bill SET title = ?, body = ?, pinned = ?, price = ? WHERE id = ?"
            db.execute(sql, (title, body, pinned, price, bill_id))
            db.commit()
            
            flash("Bill updated successfully!", "success")
            return redirect("/")
            
        
        sql = "SELECT id, title, body, pinned, price FROM bill WHERE id = ?"
        bill = db.execute(sql, (bill_id,)).fetchone()
        
        if not bill:
            flash("Bill not found!", "error")
            return redirect("/")
            
        return render_template("pages/bill_form.jinja", bill=bill)


#-----------------------------------------------------------
# Delete a Bill - Remove Bills
#-----------------------------------------------------------
@app.post("/bill/delete/<int:bill_id>")
def delete_bill(bill_id):
    with connect_db() as db:
        
        sql = "DELETE FROM bill WHERE id = ?"
        db.execute(sql, (bill_id,))
        db.commit()
        
    flash("Bill deleted successfully!", "success")
    return redirect("/")

#-----------------------------------------------------------
# Edit Balance / Amount directly 
#-----------------------------------------------------------
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

#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)
