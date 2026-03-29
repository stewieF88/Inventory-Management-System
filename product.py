from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")
SEARCH_COLUMN_MAP = {
    "Category": "Category",
    "Supplier": "Supplier",
    "Name": "name",
}


class productClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ----------- variables -------------
        self.var_cat = StringVar(value="Select")
        self.var_pid = StringVar()
        self.var_sup = StringVar(value="Select")
        self.var_name = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_status = StringVar(value="Active")
        self.var_searchby = StringVar(value="Select")
        self.var_searchtxt = StringVar()

        self.cat_list = ["Select"]
        self.sup_list = ["Select"]

        product_frame = Frame(self.root, bd=2, relief=RIDGE, bg="white")
        product_frame.place(x=10, y=10, width=450, height=480)

        # ------------ title --------------
        Label(
            product_frame,
            text="Manage Product Details",
            font=("goudy old style", 18),
            bg="#0f4d7d",
            fg="white",
        ).pack(side=TOP, fill=X)

        Label(product_frame, text="Category", font=("goudy old style", 18), bg="white").place(x=30, y=60)
        Label(product_frame, text="Supplier", font=("goudy old style", 18), bg="white").place(x=30, y=110)
        Label(product_frame, text="Name", font=("goudy old style", 18), bg="white").place(x=30, y=160)
        Label(product_frame, text="Price", font=("goudy old style", 18), bg="white").place(x=30, y=210)
        Label(product_frame, text="Quantity", font=("goudy old style", 18), bg="white").place(x=30, y=260)
        Label(product_frame, text="Status", font=("goudy old style", 18), bg="white").place(x=30, y=310)

        self.cmb_cat = ttk.Combobox(
            product_frame,
            textvariable=self.var_cat,
            values=self.cat_list,
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        self.cmb_cat.place(x=150, y=60, width=200)
        self.cmb_cat.current(0)

        self.cmb_sup = ttk.Combobox(
            product_frame,
            textvariable=self.var_sup,
            values=self.sup_list,
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        self.cmb_sup.place(x=150, y=110, width=200)
        self.cmb_sup.current(0)

        Entry(product_frame, textvariable=self.var_name, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=160, width=200
        )
        Entry(product_frame, textvariable=self.var_price, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=210, width=200
        )
        Entry(product_frame, textvariable=self.var_qty, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=260, width=200
        )

        cmb_status = ttk.Combobox(
            product_frame,
            textvariable=self.var_status,
            values=("Active", "Inactive"),
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        cmb_status.place(x=150, y=310, width=200)
        cmb_status.current(0)

        # -------------- buttons -----------------
        Button(
            product_frame,
            text="Save",
            command=self.add,
            font=("goudy old style", 15),
            bg="#2196f3",
            fg="white",
            cursor="hand2",
        ).place(x=10, y=400, width=100, height=40)
        Button(
            product_frame,
            text="Update",
            command=self.update,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=120, y=400, width=100, height=40)
        Button(
            product_frame,
            text="Delete",
            command=self.delete,
            font=("goudy old style", 15),
            bg="#f44336",
            fg="white",
            cursor="hand2",
        ).place(x=230, y=400, width=100, height=40)
        Button(
            product_frame,
            text="Clear",
            command=self.clear,
            font=("goudy old style", 15),
            bg="#607d8b",
            fg="white",
            cursor="hand2",
        ).place(x=340, y=400, width=100, height=40)

        # ---------- Search Frame -------------
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
            values=("Select", "Category", "Supplier", "Name"),
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

        # ------------ product details -------------
        table_frame = Frame(self.root, bd=3, relief=RIDGE)
        table_frame.place(x=480, y=100, width=600, height=390)

        scrolly = Scrollbar(table_frame, orient=VERTICAL)
        scrollx = Scrollbar(table_frame, orient=HORIZONTAL)

        self.ProductTable = ttk.Treeview(
            table_frame,
            columns=("pid", "Category", "Supplier", "name", "price", "qty", "status"),
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
        self.ProductTable.heading("status", text="Status")
        self.ProductTable["show"] = "headings"
        self.ProductTable.column("pid", width=90)
        self.ProductTable.column("Category", width=100)
        self.ProductTable.column("Supplier", width=100)
        self.ProductTable.column("name", width=100)
        self.ProductTable.column("price", width=100)
        self.ProductTable.column("qty", width=100)
        self.ProductTable.column("status", width=100)

        self.ProductTable.pack(fill=BOTH, expand=1)
        self.ProductTable.bind("<ButtonRelease-1>", self.get_data)

        self.fetch_cat_sup()
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
        )

    def fetch_cat_sup(self):
        try:
            self.cat_list = ["Select"]
            self.sup_list = ["Select"]

            categories = self._run_query("select name from category", fetchall=True)
            suppliers = self._run_query("select name from supplier", fetchall=True)

            self.cat_list.extend(row[0] for row in categories)
            self.sup_list.extend(row[0] for row in suppliers)

            self.cmb_cat.config(values=self.cat_list)
            self.cmb_sup.config(values=self.sup_list)

            if self.var_cat.get() not in self.cat_list:
                self.var_cat.set("Select")
            if self.var_sup.get() not in self.sup_list:
                self.var_sup.set("Select")
        except Exception as ex:
            self._handle_error(ex)

    def add(self):
        category = self.var_cat.get()
        supplier = self.var_sup.get()
        if self._selection_is_invalid(category) or self._selection_is_invalid(supplier):
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return

        try:
            product_name = self.var_name.get().strip()
            if self._run_query("select 1 from product where name=?", (product_name,), fetchone=True):
                messagebox.showerror("Error", "Product already present", parent=self.root)
                return

            self._run_query(
                "insert into product(Category,Supplier,name,price,qty,status) values(?,?,?,?,?,?)",
                self._product_values(),
            )
            messagebox.showinfo("Success", "Product Added Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def show(self):
        try:
            rows = self._run_query("select * from product", fetchall=True)
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
        self.var_status.set(row[6])

    def update(self):
        pid = self.var_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Please select product from list", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from product where pid=?", (pid,), fetchone=True):
                messagebox.showerror("Error", "Invalid Product", parent=self.root)
                return

            self._run_query(
                "update product set Category=?,Supplier=?,name=?,price=?,qty=?,status=? where pid=?",
                self._product_values() + (pid,),
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
                f"select * from product where {column_name} LIKE ?",
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
