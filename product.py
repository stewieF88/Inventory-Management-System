from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3
import time

from create_db import create_db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")
SEARCH_COLUMN_MAP = {
    "Category": "Category",
    "Supplier": "Supplier",
    "Employee": "employee",
    "Name": "name",
}


class productClass:
    def __init__(self, root):
        create_db()

        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ----------- variables -------------
        self.var_cat = StringVar(value="Select")
        self.var_pid = StringVar()
        self.var_sup = StringVar(value="Select")
        self.var_emp = StringVar(value="Select")
        self.var_name = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_status = StringVar(value="Active")
        self.var_searchby = StringVar(value="Select")
        self.var_searchtxt = StringVar()

        self.cat_list = ["Select"]
        self.sup_list = ["Select"]
        self.emp_list = ["Select"]

        product_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        product_frame.place(x=10, y=10, width=450, height=480)

        Label(
            product_frame,
            text="Manage Product Details",
            font=("goudy old style", 18),
            bg="#0f4d7d",
            fg="white",
        ).pack(side=TOP, fill=X)

        Label(product_frame, text="Category", font=("goudy old style", 16), bg="white").place(x=30, y=40)
        Label(product_frame, text="Supplier", font=("goudy old style", 16), bg="white").place(x=30, y=85)
        Label(product_frame, text="Name", font=("goudy old style", 16), bg="white").place(x=30, y=130)
        Label(product_frame, text="Price", font=("goudy old style", 16), bg="white").place(x=30, y=175)
        Label(product_frame, text="Quantity", font=("goudy old style", 16), bg="white").place(x=30, y=220)
        Label(product_frame, text="Employee", font=("goudy old style", 16), bg="white").place(x=30, y=265)
        Label(product_frame, text="Status", font=("goudy old style", 16), bg="white").place(x=30, y=310)

        self.cmb_cat = ttk.Combobox(
            product_frame,
            textvariable=self.var_cat,
            values=self.cat_list,
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 14),
        )
        self.cmb_cat.place(x=150, y=40, width=260)
        self.cmb_cat.current(0)

        self.cmb_sup = ttk.Combobox(
            product_frame,
            textvariable=self.var_sup,
            values=self.sup_list,
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 14),
        )
        self.cmb_sup.place(x=150, y=85, width=260)
        self.cmb_sup.current(0)

        Entry(product_frame, textvariable=self.var_name, font=("goudy old style", 14), bg="lightyellow").place(
            x=150, y=130, width=260
        )
        Entry(product_frame, textvariable=self.var_price, font=("goudy old style", 14), bg="lightyellow").place(
            x=150, y=175, width=260
        )
        Entry(product_frame, textvariable=self.var_qty, font=("goudy old style", 14), bg="lightyellow").place(
            x=150, y=220, width=260
        )

        self.cmb_emp = ttk.Combobox(
            product_frame,
            textvariable=self.var_emp,
            values=self.emp_list,
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 14),
        )
        self.cmb_emp.place(x=150, y=265, width=260)
        self.cmb_emp.current(0)

        cmb_status = ttk.Combobox(
            product_frame,
            textvariable=self.var_status,
            values=("Active", "Inactive"),
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 14),
        )
        cmb_status.place(x=150, y=310, width=260)
        cmb_status.current(0)

        Button(
            product_frame,
            text="Save",
            command=self.add,
            font=("goudy old style", 15),
            bg="#2196f3",
            fg="white",
            cursor="hand2",
        ).place(x=10, y=380, width=100, height=40)
        Button(
            product_frame,
            text="Update",
            command=self.update,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=120, y=380, width=100, height=40)
        Button(
            product_frame,
            text="Delete",
            command=self.delete,
            font=("goudy old style", 15),
            bg="#f44336",
            fg="white",
            cursor="hand2",
        ).place(x=230, y=380, width=100, height=40)
        Button(
            product_frame,
            text="Clear",
            command=self.clear,
            font=("goudy old style", 15),
            bg="#607d8b",
            fg="white",
            cursor="hand2",
        ).place(x=340, y=380, width=100, height=40)

        search_frame = LabelFrame(
            self.root,
            text="Search Product",
            font=("goudy old style", 12, "bold"),
            bd=2,
            relief=RIDGE,
            bg="white",
        )
        search_frame.place(x=480, y=10, width=600, height=80)

        cmb_search = ttk.Combobox(
            search_frame,
            textvariable=self.var_searchby,
            values=("Select", "Category", "Supplier", "Employee", "Name"),
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        cmb_search.place(x=10, y=10, width=180)
        cmb_search.current(0)

        Entry(search_frame, textvariable=self.var_searchtxt, font=("goudy old style", 15), bg="lightyellow").place(
            x=200, y=10
        )
        Button(
            search_frame,
            text="Search",
            command=self.search,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=410, y=9, width=150, height=30)

        table_frame = Frame(self.root, bd=3, relief=RIDGE)
        table_frame.place(x=480, y=100, width=600, height=390)

        scrolly = Scrollbar(table_frame, orient=VERTICAL)
        scrollx = Scrollbar(table_frame, orient=HORIZONTAL)

        self.ProductTable = ttk.Treeview(
            table_frame,
            columns=("pid", "Category", "Supplier", "name", "price", "qty", "employee", "status"),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set,
        )
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.ProductTable.xview)
        scrolly.config(command=self.ProductTable.yview)
        self.ProductTable.heading("pid", text="P ID")
        self.ProductTable.heading("Category", text="Category")
        self.ProductTable.heading("Supplier", text="Supplier")
        self.ProductTable.heading("name", text="Name")
        self.ProductTable.heading("price", text="Price")
        self.ProductTable.heading("qty", text="Quantity")
        self.ProductTable.heading("employee", text="Employee")
        self.ProductTable.heading("status", text="Status")
        self.ProductTable["show"] = "headings"
        self.ProductTable["displaycolumns"] = ("pid", "Category", "name", "price", "qty", "status")
        self.ProductTable.column("pid", width=60)
        self.ProductTable.column("Category", width=90)
        self.ProductTable.column("Supplier", width=90)
        self.ProductTable.column("name", width=95)
        self.ProductTable.column("price", width=75)
        self.ProductTable.column("qty", width=75)
        self.ProductTable.column("employee", width=95)
        self.ProductTable.column("status", width=75)

        self.ProductTable.pack(fill=BOTH, expand=1)
        self.ProductTable.bind("<ButtonRelease-1>", self.get_data)

        self.fetch_lookup_data()
        self.show()

    # -----------------------------------------------------------------------------------------------------
    def _run_query(self, query, params=(), *, fetchone=False, fetchall=False):
        with sqlite3.connect(database=DB_PATH) as con:
            cur = con.cursor()
            cur.execute(query, params)
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            con.commit()
            return None

    def _handle_error(self, error):
        messagebox.showerror("Error", f"Error due to : {error}", parent=self.root)

    def _populate_product_table(self, rows):
        self.ProductTable.delete(*self.ProductTable.get_children())
        for row in rows:
            self.ProductTable.insert("", END, values=row)

    def _selected_product_row(self):
        focused_item = self.ProductTable.focus()
        if not focused_item:
            return None
        row = self.ProductTable.item(focused_item).get("values", [])
        return row if row else None

    def _selection_is_invalid(self, value):
        return value in ("", "Select", "Empty")

    def _product_values(self):
        return (
            self.var_cat.get(),
            self.var_sup.get(),
            self.var_name.get().strip(),
            self.var_price.get().strip(),
            self.var_qty.get().strip(),
            self.var_status.get(),
            self.var_emp.get(),
        )

    def _safe_int(self, value, default=0):
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return default

    def _validated_price_qty(self):
        try:
            price = float(self.var_price.get().strip())
            qty = int(self.var_qty.get().strip())
        except ValueError:
            messagebox.showerror(
                "Error",
                "Price must be numeric and quantity must be a whole number",
                parent=self.root,
            )
            return None

        if price < 0 or qty < 0:
            messagebox.showerror("Error", "Price and quantity cannot be negative", parent=self.root)
            return None
        return price, qty

    def _log_inventory_history(
        self,
        *,
        source,
        reference,
        employee,
        supplier,
        product_id,
        product_name,
        category,
        quantity,
        unit_price,
    ):
        if quantity == 0:
            return

        line_total = float(quantity) * float(unit_price)
        self._run_query(
            "insert into inventory_history(source,reference,employee,supplier,product_id,product_name,category,quantity,unit_price,line_total,trans_date,trans_time) "
            "values(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                source,
                reference,
                employee,
                supplier,
                int(product_id),
                product_name,
                category,
                int(quantity),
                float(unit_price),
                line_total,
                time.strftime("%d/%m/%Y"),
                time.strftime("%H:%M:%S"),
            ),
        )

    def fetch_lookup_data(self):
        try:
            self.cat_list = ["Select"]
            self.sup_list = ["Select"]
            self.emp_list = ["Select"]

            categories = self._run_query("select name from category order by name", fetchall=True)
            suppliers = self._run_query("select name from supplier order by name", fetchall=True)
            employees = self._run_query("select name from employee order by name", fetchall=True)

            self.cat_list.extend(row[0] for row in categories)
            self.sup_list.extend(row[0] for row in suppliers)
            self.emp_list.extend(row[0] for row in employees)

            self.cmb_cat.config(values=self.cat_list)
            self.cmb_sup.config(values=self.sup_list)
            self.cmb_emp.config(values=self.emp_list)

            if self.var_cat.get() not in self.cat_list:
                self.var_cat.set("Select")
            if self.var_sup.get() not in self.sup_list:
                self.var_sup.set("Select")
            if self.var_emp.get() not in self.emp_list:
                self.var_emp.set("Select")
        except Exception as ex:
            self._handle_error(ex)

    # Backward compatible name used in older code.
    def fetch_cat_sup(self):
        self.fetch_lookup_data()

    def add(self):
        category = self.var_cat.get()
        supplier = self.var_sup.get()
        employee = self.var_emp.get()
        product_name = self.var_name.get().strip()

        if (
            self._selection_is_invalid(category)
            or self._selection_is_invalid(supplier)
            or self._selection_is_invalid(employee)
            or not product_name
        ):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return

        validated = self._validated_price_qty()
        if not validated:
            return
        unit_price, quantity = validated

        try:
            if self._run_query("select 1 from product where name=?", (product_name,), fetchone=True):
                messagebox.showerror("Error", "Product already present", parent=self.root)
                return

            self._run_query(
                "insert into product(Category,Supplier,name,price,qty,status,employee) values(?,?,?,?,?,?,?)",
                self._product_values(),
            )
            row = self._run_query("select pid from product where name=?", (product_name,), fetchone=True)
            if row:
                self._log_inventory_history(
                    source="PRODUCT",
                    reference="STOCK-IN",
                    employee=employee,
                    supplier=supplier,
                    product_id=row[0],
                    product_name=product_name,
                    category=category,
                    quantity=quantity,
                    unit_price=unit_price,
                )
            messagebox.showinfo("Success", "Product Added Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def show(self):
        try:
            rows = self._run_query(
                "select pid,Category,Supplier,name,price,qty,employee,status from product",
                fetchall=True,
            )
            self._populate_product_table(rows)
        except Exception as ex:
            self._handle_error(ex)

    def get_data(self, _event):
        row = self._selected_product_row()
        if not row:
            return

        self.var_pid.set(row[0])
        self.var_cat.set(row[1])
        self.var_sup.set(row[2])
        self.var_name.set(row[3])
        self.var_price.set(row[4])
        self.var_qty.set(row[5])
        self.var_emp.set(row[6])
        self.var_status.set(row[7])

    def update(self):
        pid = self.var_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Please select product from list", parent=self.root)
            return

        validated = self._validated_price_qty()
        if not validated:
            return
        unit_price, new_qty = validated
        category = self.var_cat.get()
        supplier = self.var_sup.get()
        employee = self.var_emp.get()
        product_name = self.var_name.get().strip()

        try:
            old_row = self._run_query(
                "select qty from product where pid=?",
                (pid,),
                fetchone=True,
            )
            if not old_row:
                messagebox.showerror("Error", "Invalid Product", parent=self.root)
                return

            self._run_query(
                "update product set Category=?,Supplier=?,name=?,price=?,qty=?,status=?,employee=? where pid=?",
                self._product_values() + (pid,),
            )
            qty_diff = new_qty - self._safe_int(old_row[0], default=0)
            if qty_diff != 0:
                self._log_inventory_history(
                    source="PRODUCT",
                    reference="STOCK-ADJUST",
                    employee=employee,
                    supplier=supplier,
                    product_id=pid,
                    product_name=product_name,
                    category=category,
                    quantity=qty_diff,
                    unit_price=unit_price,
                )
            messagebox.showinfo("Success", "Product Updated Successfully", parent=self.root)
            self.show()
        except Exception as ex:
            self._handle_error(ex)

    def delete(self):
        pid = self.var_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Select Product from the list", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from product where pid=?", (pid,), fetchone=True):
                messagebox.showerror("Error", "Invalid Product", parent=self.root)
                return

            if not messagebox.askyesno("Confirm", "Do you really want to delete?", parent=self.root):
                return

            self._run_query("delete from product where pid=?", (pid,))
            messagebox.showinfo("Delete", "Product Deleted Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def clear(self):
        self.var_cat.set("Select")
        self.var_sup.set("Select")
        self.var_emp.set("Select")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.var_status.set("Active")
        self.var_pid.set("")
        self.var_searchby.set("Select")
        self.var_searchtxt.set("")
        self.show()

    def search(self):
        search_by = self.var_searchby.get()
        search_text = self.var_searchtxt.get().strip()

        if search_by == "Select":
            messagebox.showerror("Error", "Select Search By option", parent=self.root)
            return
        if not search_text:
            messagebox.showerror("Error", "Search input should be required", parent=self.root)
            return

        column_name = SEARCH_COLUMN_MAP.get(search_by)
        if not column_name:
            messagebox.showerror("Error", "Invalid Search By option", parent=self.root)
            return

        try:
            rows = self._run_query(
                f"select pid,Category,Supplier,name,price,qty,employee,status from product where {column_name} LIKE ?",
                (f"%{search_text}%",),
                fetchall=True,
            )
            if rows:
                self._populate_product_table(rows)
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)
        except Exception as ex:
            self._handle_error(ex)


if __name__ == "__main__":
    root = Tk()
    obj = productClass(root)
    root.mainloop()
