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
# Home page - Show all Bills
#-----------------------------------------------------------
@app.get("/")
def show_bills():
    with connect_db() as db:
        sql = """
            SELECT id, title, body, pinned, created
            FROM note
            ORDER BY pinned DESC, created DESC
        """
        params = ()
        bills = db.execute(sql, params).fetchall()

        return render_template("pages/bill_list.jinja", bills=bills)
    
#-----------------------------------------------------------
# Add a new Bill - Add new Bills
#-----------------------------------------------------------
@app.route("/bill/add", methods=["GET", "POST"])
def add_bill():
    if request.method == "POST":
        title = html.escape(request.form.get("title", "").strip())
        body = html.escape(request.form.get("body", "").strip())

        # If the checkbox is checked, pinned = 1; otherwise pinned = 0
        pinned = 1 if request.form.get("pinned") else 0
        
        if not title:
            flash("Title is required!", "error")
            return redirect("/bill/add")

        with connect_db() as db:
            sql = "INSERT INTO note (title, body, pinned) VALUES (?, ?, ?)"
            db.execute(sql, (title, body, pinned))
            db.commit()
            
        flash("Bill added successfully!", "success")
        return redirect("/")
        
    return render_template("pages/bill_form.jinja", bill=None)

#-----------------------------------------------------------
# Edit an existing Bill
#-----------------------------------------------------------
@app.route("/bill/edit/<int:bill_id>", methods=["GET", "POST"])
def edit_bill(bill_id):
    with connect_db() as db:
        if request.method == "POST":
            title = html.escape(request.form.get("title", "").strip())
            body = html.escape(request.form.get("body", "").strip())
            
            # If the checkbox is checked, it will equal "1". If unchecked, it will be 0.
            pinned = 1 if request.form.get("pinned") else 0
            
            if not title:
                flash("Title is required!", "error")
                return redirect(f"/bill/edit/{bill_id}")

            # Update the statement to include pinned
            sql = "UPDATE note SET title = ?, body = ?, pinned = ? WHERE id = ?"
            db.execute(sql, (title, body, pinned, bill_id))
            db.commit()
            
            flash("Bill updated successfully!", "success")
            return redirect("/")
            
        # GET request: Fetch existing row data to pre-populate fields
        sql = "SELECT id, title, body, pinned FROM note WHERE id = ?"
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
        sql = "DELETE FROM note WHERE id = ?"
        db.execute(sql, (bill_id,))
        db.commit()
        
    flash("Bill deleted successfully!", "success")
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

