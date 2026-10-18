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

    # FIXED: Added the real price tracking column right inside your layout
    SCHEMA = """
        CREATE TABLE bill (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            body    TEXT,
            pinned  INTEGER DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            price   REAL DEFAULT 0.00
        )
    """

    # FIXED: Updated sample columns and seeds to populate with sample dollar amounts!
    SEED_DATA = """
        INSERT INTO bill (title, pinned, body, price)
        VALUES
            ("Welcome!",      1, "This is a demo application using Flask, Jinja and SQLite.", 0.00),
            ("Shopping List", 0, "Milk\nBread\nEggs\nCheese", 42.50),
            ("Power Bill",    0, "Due next week.\n\nAccount: 123-45678-90", 185.20),
            ("Internet",      0, "Monthly fibre connection subscription plan fee.", 89.00),
            ("Important!",    1, "Remember to backup your database regularly.", 0.00)
    """

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
