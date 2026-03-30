import gc
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

import billing
import create_db
import sales


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class DummyLabel:
    def __init__(self):
        self.text = ""

    def config(self, **kwargs):
        if "text" in kwargs:
            self.text = kwargs["text"]


class DummyText:
    def __init__(self):
        self.content = ""

    def delete(self, *_args, **_kwargs):
        self.content = ""

    def insert(self, *_args):
        if len(_args) >= 2:
            self.content += str(_args[1])

    def get(self):
        return self.content


class DummyListbox:
    def __init__(self):
        self.items = []
        self._selection = ()

    def delete(self, *_args, **_kwargs):
        self.items = []

    def insert(self, _index, value):
        self.items.append(value)

    def curselection(self):
        return self._selection

    def get(self, selection):
        if isinstance(selection, tuple):
            selection = selection[0]
        return self.items[selection]


class DummyTree:
    def __init__(self):
        self.rows = []

    def delete(self, *_args, **_kwargs):
        self.rows = []

    def get_children(self):
        return list(range(len(self.rows)))

    def insert(self, _parent, _index, values=()):
        self.rows.append(values)


class BillingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = os.path.join(self.temp_dir.name, "ims_test.db")
        self.test_bill_dir = os.path.join(self.temp_dir.name, "bill")
        os.makedirs(self.test_bill_dir, exist_ok=True)

        # Patch module-level paths used by the project.
        self.original_create_db_path = create_db.DB_PATH
        self.original_billing_db_path = billing.DB_PATH
        self.original_billing_bill_dir = billing.BILL_DIR
        self.original_sales_db_path = sales.DB_PATH
        self.original_sales_bill_dir = sales.BILL_DIR

        create_db.DB_PATH = self.test_db
        billing.DB_PATH = self.test_db
        billing.BILL_DIR = self.test_bill_dir
        sales.DB_PATH = self.test_db
        sales.BILL_DIR = self.test_bill_dir

        create_db.create_db()
        self._seed_master_data()

    def tearDown(self):
        create_db.DB_PATH = self.original_create_db_path
        billing.DB_PATH = self.original_billing_db_path
        billing.BILL_DIR = self.original_billing_bill_dir
        sales.DB_PATH = self.original_sales_db_path
        sales.BILL_DIR = self.original_sales_bill_dir
        gc.collect()
        self.temp_dir.cleanup()

    def _seed_master_data(self):
        with sqlite3.connect(self.test_db) as con:
            cur = con.cursor()

            employees = [
                ("Adam", "adam@test.com", "Male", "111111", "2000-01-01", "2024-01-01", "pass", "Admin", "Address 1", "1000"),
                ("Bob", "bob@test.com", "Male", "222222", "2000-02-02", "2024-01-02", "pass", "Admin", "Address 2", "1100"),
                ("Cecilia", "cecilia@test.com", "Female", "333333", "2000-03-03", "2024-01-03", "pass", "Admin", "Address 3", "1200"),
            ]
            cur.executemany(
                "insert into employee(name,email,gender,contact,dob,doj,pass,utype,address,salary) values(?,?,?,?,?,?,?,?,?,?)",
                employees,
            )

            suppliers = [
                (1, "Supplier01", "555001", "Main supplier"),
                (2, "Supplier02", "555002", "Backup supplier"),
            ]
            cur.executemany(
                "insert into supplier(invoice,name,contact,desc) values(?,?,?,?)",
                suppliers,
            )

            categories = [("Category01",), ("Category02",)]
            cur.executemany("insert into category(name) values(?)", categories)

            products = [
                ("Category01", "Supplier01", "Product01", "100", "10", "Active", "Adam"),
                ("Category02", "Supplier02", "Product02", "50", "5", "Active", "Bob"),
                ("Category01", "Supplier01", "Product03", "30", "1", "Active", "Cecilia"),
            ]
            cur.executemany(
                "insert into product(Category,Supplier,name,price,qty,status,employee) values(?,?,?,?,?,?,?)",
                products,
            )
            con.commit()

    def _make_bill_obj(self):
        obj = billing.billClass.__new__(billing.billClass)
        obj.root = None
        obj.cart_items = {}
        obj.customer_map = {}
        obj.chk_print = 0

        obj.var_customer_select = DummyVar("Select")
        obj.var_cname = DummyVar("")
        obj.var_contact = DummyVar("")
        obj.var_employee = DummyVar("Select")
        obj.var_pid = DummyVar("")
        obj.var_pname = DummyVar("")
        obj.var_price = DummyVar("")
        obj.var_stock = DummyVar("")
        obj.var_qty = DummyVar("1")
        obj.var_selected_category = DummyVar("")
        obj.var_selected_supplier = DummyVar("")

        obj.lbl_amnt = DummyLabel()
        obj.lbl_net_pay = DummyLabel()
        obj.cartTitle = DummyLabel()
        obj.lbl_instock = DummyLabel()
        obj.lbl_category = DummyLabel()
        obj.txt_bill_area = DummyText()

        obj.show_cart = lambda: None
        obj.show_products = Mock()
        obj._load_lookup_data = Mock()
        return obj

    def _make_sales_obj(self):
        obj = sales.salesClass.__new__(sales.salesClass)
        obj.root = None
        obj.invoice_list = []
        obj.var_invoice = DummyVar("")
        obj.var_filter_by = DummyVar("Select")
        obj.var_filter_txt = DummyVar("")
        obj.Sales_List = DummyListbox()
        obj.HistoryTable = DummyTree()
        obj.bill_area = DummyText()
        return obj

    # -------------------- Unit tests --------------------
    def test_bill_update_calculates_totals(self):
        obj = self._make_bill_obj()
        obj.cart_items = {
            "1": {"pid": "1", "name": "Product01", "price": 100.0, "qty": 2, "stock": 10, "category": "Category01", "supplier": "Supplier01"},
            "2": {"pid": "2", "name": "Product02", "price": 50.0, "qty": 1, "stock": 5, "category": "Category02", "supplier": "Supplier02"},
        }

        billing.billClass.bill_update(obj)

        self.assertEqual(obj.bill_amnt, 250.0)
        self.assertEqual(obj.discount, 12.5)
        self.assertEqual(obj.net_pay, 237.5)
        self.assertIn("250.00", obj.lbl_amnt.text)
        self.assertIn("237.50", obj.lbl_net_pay.text)

    def test_get_or_create_customer_creates_then_reuses_customer(self):
        obj = self._make_bill_obj()
        with sqlite3.connect(self.test_db) as con:
            cur = con.cursor()
            customer_id, created = billing.billClass._get_or_create_customer(obj, cur, "Alice", "999999")
            same_customer_id, created_again = billing.billClass._get_or_create_customer(obj, cur, "Alice", "999999")
            con.commit()

        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(customer_id, same_customer_id)

    def test_add_update_cart_adds_and_removes_item(self):
        obj = self._make_bill_obj()
        obj.var_pid.set("1")
        obj.var_pname.set("Product01")
        obj.var_price.set("100")
        obj.var_stock.set("10")
        obj.var_qty.set("2")
        obj.var_selected_category.set("Category01")
        obj.var_selected_supplier.set("Supplier01")

        billing.billClass.add_update_cart(obj)
        self.assertIn("1", obj.cart_items)
        self.assertEqual(obj.cart_items["1"]["qty"], 2)

        obj.var_qty.set("0")
        billing.billClass.add_update_cart(obj)
        self.assertNotIn("1", obj.cart_items)

    # -------------------- Integration tests --------------------
    @patch("billing.messagebox.showerror")
    @patch("billing.messagebox.showinfo")
    def test_generate_bill_updates_database_and_creates_file(self, mock_info, mock_error):
        obj = self._make_bill_obj()
        obj.var_cname.set("Customer01")
        obj.var_contact.set("900001")
        obj.var_employee.set("Adam")
        obj.cart_items = {
            "1": {"pid": "1", "name": "Product01", "price": 100.0, "qty": 2, "stock": 10, "category": "Category01", "supplier": "Supplier01"}
        }
        billing.billClass.bill_update(obj)

        billing.billClass.generate_bill(obj)

        self.assertEqual(mock_error.call_count, 0)
        self.assertEqual(obj.chk_print, 1)
        self.assertIn("Customer Name: Customer01", obj.txt_bill_area.get())

        with sqlite3.connect(self.test_db) as con:
            cur = con.cursor()
            cur.execute("select count(*) from customer where name=? and contact=?", ("Customer01", "900001"))
            self.assertEqual(cur.fetchone()[0], 1)

            cur.execute("select qty,status from product where pid=1")
            qty, status = cur.fetchone()
            self.assertEqual(qty, "8")
            self.assertEqual(status, "Active")

            cur.execute("select invoice,bill_file,employee,product_name,category,quantity,discount,net_pay from sales_history")
            history = cur.fetchone()
            self.assertIsNotNone(history)
            self.assertEqual(history[2], "Adam")
            self.assertEqual(history[3], "Product01")
            self.assertEqual(history[4], "Category01")
            self.assertEqual(history[5], 2)
            self.assertEqual(history[6], 10.0)
            self.assertEqual(history[7], 190.0)
            invoice = history[0]
            bill_file = history[1]

        self.assertTrue(os.path.exists(os.path.join(self.test_bill_dir, bill_file)))
        self.assertTrue(invoice in bill_file)
        mock_info.assert_called_once()

    @patch("billing.messagebox.showerror")
    @patch("billing.messagebox.showinfo")
    def test_generated_bill_is_visible_in_sales_module_filter(self, _mock_info, _mock_error):
        bill_obj = self._make_bill_obj()
        bill_obj.var_cname.set("Customer02")
        bill_obj.var_contact.set("900002")
        bill_obj.var_employee.set("Bob")
        bill_obj.cart_items = {
            "2": {"pid": "2", "name": "Product02", "price": 50.0, "qty": 1, "stock": 5, "category": "Category02", "supplier": "Supplier02"}
        }
        billing.billClass.bill_update(bill_obj)
        billing.billClass.generate_bill(bill_obj)

        sales_obj = self._make_sales_obj()
        sales.salesClass._load_invoices(sales_obj, "Employee", "Bob")
        sales.salesClass._load_transactions(sales_obj, "Employee", "Bob")

        self.assertEqual(len(sales_obj.invoice_list), 1)
        self.assertEqual(len(sales_obj.HistoryTable.rows), 1)
        self.assertEqual(sales_obj.HistoryTable.rows[0][2], "Bob")
        self.assertEqual(sales_obj.HistoryTable.rows[0][4], "Product02")

        invoice = sales_obj.invoice_list[0]
        sales.salesClass._display_invoice(sales_obj, invoice)
        self.assertIn("Customer Name: Customer02", sales_obj.bill_area.get())

    # -------------------- Regression test --------------------
    def test_regression_fixed_discount_rule_is_still_5_percent(self):
        """
        This regression test protects the current billing rule.
        If the project later changes from a fixed discount to configurable discounts,
        this test would become obsolete and should be replaced by a rule-based test.
        """
        obj = self._make_bill_obj()
        obj.cart_items = {
            "3": {"pid": "3", "name": "Product03", "price": 30.0, "qty": 1, "stock": 1, "category": "Category01", "supplier": "Supplier01"},
            "1": {"pid": "1", "name": "Product01", "price": 100.0, "qty": 1, "stock": 10, "category": "Category01", "supplier": "Supplier01"},
        }

        billing.billClass.bill_update(obj)

        self.assertEqual(obj.bill_amnt, 130.0)
        self.assertEqual(obj.discount, 6.5)
        self.assertEqual(obj.net_pay, 123.5)


if __name__ == "__main__":
    unittest.main()
