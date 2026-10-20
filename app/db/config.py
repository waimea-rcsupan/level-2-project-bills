#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class BillTable:

    NAME = "bill"

    SCHEMA = """
        CREATE TABLE bill (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            body    TEXT,
            pinned  INTEGER DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            price   REAL DEFAULT 0.00,
            due_date TEXT
        )
    """

    SEED_DATA = """
        INSERT INTO bill (title, pinned, body, price, due_date)
        VALUES
            ("Welcome!",      1, "This is a demo application using Flask, Jinja and SQLite.", 0.00, "2026-10-31"),
            ("Shopping List", 0, "Milk\nBread\nEggs\nCheese", 42.50, "2026-10-25"),
            ("Power Bill",    0, "Due next week.\n\nAccount: 123-45678-90", 185.20, "2026-10-27"),
            ("Internet",      0, "Monthly fibre connection subscription plan fee.", 89.00, "2026-11-01"),
            ("Important!",    1, "Remember to backup your database regularly.", 0.00, "")
    """

TABLES = [
    BillTable,
]
# Add more table classes here...



#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    BillTable,
    # Add more tables here...
]
