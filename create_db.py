import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")


def _column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns


def create_db():
    with sqlite3.connect(database=DB_PATH) as con:
        cur = con.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS employee("
            "eid INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name text,email text,gender text,contact text,dob text,doj text,"
            "pass text,utype text,address text,salary text)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS supplier("
            "invoice INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name text,contact text,desc text)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS category("
            "cid INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name text)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS product("
            "pid INTEGER PRIMARY KEY AUTOINCREMENT,"
            "Category text,Supplier text,name text,price text,qty text,status text,employee text)"
        )

        # Existing databases can already have the product table without employee.
        if not _column_exists(cur, "product", "employee"):
            cur.execute("ALTER TABLE product ADD COLUMN employee text")

        cur.execute(
            "CREATE TABLE IF NOT EXISTS customer("
            "cid INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name text NOT NULL,"
            "contact text NOT NULL,"
            "UNIQUE(name, contact))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS sales_history("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "invoice text NOT NULL,"
            "bill_file text NOT NULL,"
            "customer_id INTEGER,"
            "customer_name text,"
            "customer_contact text,"
            "employee text,"
            "supplier text,"
            "product_id INTEGER,"
            "product_name text,"
            "category text,"
            "quantity INTEGER,"
            "unit_price REAL,"
            "line_total REAL,"
            "bill_amount REAL,"
            "discount REAL,"
            "net_pay REAL,"
            "bill_date text,"
            "bill_time text)"
        )

        # Existing databases can already have sales_history without supplier.
        if not _column_exists(cur, "sales_history", "supplier"):
            cur.execute("ALTER TABLE sales_history ADD COLUMN supplier text")

        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_history_invoice ON sales_history(invoice)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_history_employee ON sales_history(employee)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_history_supplier ON sales_history(supplier)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_history_product_name ON sales_history(product_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_history_category ON sales_history(category)")
        con.commit()


if __name__ == "__main__":
    create_db()
