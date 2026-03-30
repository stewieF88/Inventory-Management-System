from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3
import tempfile
import time

from create_db import create_db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
DB_PATH = os.path.join(BASE_DIR, "ims.db")
BILL_DIR = os.path.join(BASE_DIR, "bill")
DISCOUNT_PERCENT = 5

os.makedirs(BILL_DIR, exist_ok=True)


class billClass:
    def __init__(self, root):
        create_db()

        self.root = root
        self.root.geometry("1350x700+110+80")
        self.root.resizable(False, False)
        self.root.config(bg="white")

        self.cart_items = {}
        self.customer_map = {}
        self.chk_print = 0

        self.var_search = StringVar()
        self.var_category = StringVar(value="All")
        self.var_customer_select = StringVar(value="Select")
        self.var_cname = StringVar()
        self.var_contact = StringVar()
        self.var_employee = StringVar(value="Select")
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = StringVar()
        self.var_stock = StringVar()
        self.var_qty = StringVar(value="1")
        self.var_selected_category = StringVar()
        self.var_selected_supplier = StringVar()

        self._build_ui()
        self._load_lookup_data()
        self.show_products()
        self.show_cart()
        self.bill_update()
        self.update_date_time()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        self.icon_title = PhotoImage(file=os.path.join(IMAGE_DIR, "logo1.png"))
        Label(
            self.root,
            text="Inventory Management System",
            image=self.icon_title,
            compound=LEFT,
            font=("times new roman", 40, "bold"),
            bg="#010c48",
            fg="white",
            anchor="w",
            padx=20,
        ).place(x=0, y=0, relwidth=1, height=70)

        self.lbl_clock = Label(
            self.root,
            text="Welcome to Inventory Management System\t\t Date: DD:MM:YYYY\t\t Time: HH:MM:SS",
            font=("times new roman", 15),
            bg="#4d636d",
            fg="white",
        )
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)

        product_frame = LabelFrame(self.root, text="Products", font=("goudy old style", 14, "bold"), bg="white")
        product_frame.place(x=10, y=110, width=430, height=550)

        Label(product_frame, text="Name", bg="white", font=("times new roman", 13)).place(x=10, y=10)
        Entry(product_frame, textvariable=self.var_search, bg="lightyellow", font=("times new roman", 12)).place(x=70, y=10, width=130)
        Label(product_frame, text="Category", bg="white", font=("times new roman", 13)).place(x=210, y=10)
        self.cmb_category = ttk.Combobox(product_frame, textvariable=self.var_category, state="readonly", justify=CENTER, font=("times new roman", 11))
        self.cmb_category.place(x=285, y=10, width=130)
        Button(product_frame, text="Search", command=self.search, bg="#2196f3", fg="white").place(x=10, y=42, width=90, height=24)
        Button(product_frame, text="Show All", command=self.show, bg="#083531", fg="white").place(x=110, y=42, width=90, height=24)

        table_frame = Frame(product_frame, bd=2, relief=RIDGE)
        table_frame.place(x=10, y=76, width=405, height=290)
        yscroll = Scrollbar(table_frame, orient=VERTICAL)
        xscroll = Scrollbar(table_frame, orient=HORIZONTAL)
        self.product_Table = ttk.Treeview(
            table_frame,
            columns=("pid", "category", "supplier", "name", "price", "qty", "employee"),
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set,
        )
        yscroll.pack(side=RIGHT, fill=Y)
        xscroll.pack(side=BOTTOM, fill=X)
        yscroll.config(command=self.product_Table.yview)
        xscroll.config(command=self.product_Table.xview)
        self.product_Table.heading("pid", text="P ID")
        self.product_Table.heading("category", text="Category")
        self.product_Table.heading("supplier", text="Supplier")
        self.product_Table.heading("name", text="Name")
        self.product_Table.heading("price", text="Price")
        self.product_Table.heading("qty", text="Qty")
        self.product_Table.heading("employee", text="Employee")
        self.product_Table["show"] = "headings"
        self.product_Table["displaycolumns"] = ("pid", "category", "supplier", "name", "price", "qty")
        self.product_Table.column("pid", width=40)
        self.product_Table.column("category", width=75)
        self.product_Table.column("supplier", width=80)
        self.product_Table.column("name", width=80)
        self.product_Table.column("price", width=60)
        self.product_Table.column("qty", width=45)
        self.product_Table.column("employee", width=90)
        self.product_Table.pack(fill=BOTH, expand=1)
        self.product_Table.bind("<ButtonRelease-1>", self.get_data)

        Label(product_frame, text="Product", bg="white", font=("times new roman", 13)).place(x=10, y=380)
        Entry(product_frame, textvariable=self.var_pname, bg="lightyellow", state="readonly").place(x=80, y=380, width=130)
        Label(product_frame, text="Price", bg="white", font=("times new roman", 13)).place(x=220, y=380)
        Entry(product_frame, textvariable=self.var_price, bg="lightyellow", state="readonly").place(x=270, y=380, width=60)
        Label(product_frame, text="Qty", bg="white", font=("times new roman", 13)).place(x=335, y=380)
        Entry(product_frame, textvariable=self.var_qty, bg="lightyellow").place(x=370, y=380, width=45)

        self.lbl_instock = Label(product_frame, text="In Stock", bg="white", font=("times new roman", 12))
        self.lbl_instock.place(x=10, y=415)
        self.lbl_category = Label(product_frame, text="Category", bg="white", font=("times new roman", 12))
        self.lbl_category.place(x=150, y=415)
        Button(product_frame, text="Add | Update", command=self.add_update_cart, bg="orange").place(x=10, y=455, width=195, height=30)
        Button(product_frame, text="Clear Product", command=self.clear_cart, bg="lightgray").place(x=220, y=455, width=195, height=30)
        Label(product_frame, text="Set quantity to 0 to remove from cart", bg="white", fg="red", font=("times new roman", 11)).place(x=10, y=495)

        customer_frame = LabelFrame(self.root, text="Customer + Employee", font=("goudy old style", 14, "bold"), bg="white")
        customer_frame.place(x=450, y=110, width=450, height=150)
        Label(customer_frame, text="Customer", bg="white", font=("times new roman", 13)).place(x=10, y=10)
        self.cmb_customer = ttk.Combobox(customer_frame, textvariable=self.var_customer_select, state="readonly", font=("times new roman", 11))
        self.cmb_customer.place(x=90, y=10, width=220)
        self.cmb_customer.bind("<<ComboboxSelected>>", self.on_customer_select)
        Label(customer_frame, text="Employee", bg="white", font=("times new roman", 13)).place(x=320, y=10)
        self.cmb_employee = ttk.Combobox(customer_frame, textvariable=self.var_employee, state="readonly", justify=CENTER, font=("times new roman", 11))
        self.cmb_employee.place(x=320, y=35, width=120)
        Label(customer_frame, text="Name", bg="white", font=("times new roman", 13)).place(x=10, y=70)
        Entry(customer_frame, textvariable=self.var_cname, bg="lightyellow").place(x=90, y=70, width=220)
        Label(customer_frame, text="Contact", bg="white", font=("times new roman", 13)).place(x=10, y=105)
        Entry(customer_frame, textvariable=self.var_contact, bg="lightyellow").place(x=90, y=105, width=220)

        cart_frame = LabelFrame(self.root, text="Cart", font=("goudy old style", 14, "bold"), bg="white")
        cart_frame.place(x=450, y=270, width=450, height=390)
        self.cartTitle = Label(cart_frame, text="Total Products: [0]", bg="lightgray", font=("times new roman", 12, "bold"))
        self.cartTitle.pack(side=TOP, fill=X)
        cart_inner = Frame(cart_frame, bd=2, relief=RIDGE)
        cart_inner.place(x=10, y=35, width=425, height=300)
        cy = Scrollbar(cart_inner, orient=VERTICAL)
        cx = Scrollbar(cart_inner, orient=HORIZONTAL)
        self.CartTable = ttk.Treeview(cart_inner, columns=("pid", "name", "price", "qty", "category"), yscrollcommand=cy.set, xscrollcommand=cx.set)
        cy.pack(side=RIGHT, fill=Y)
        cx.pack(side=BOTTOM, fill=X)
        cy.config(command=self.CartTable.yview)
        cx.config(command=self.CartTable.xview)
        for col, text, width in (("pid", "P ID", 40), ("name", "Name", 90), ("price", "Price", 70), ("qty", "Qty", 50), ("category", "Category", 100)):
            self.CartTable.heading(col, text=text)
            self.CartTable.column(col, width=width)
        self.CartTable["show"] = "headings"
        self.CartTable.pack(fill=BOTH, expand=1)
        self.CartTable.bind("<ButtonRelease-1>", self.get_data_cart)
        Button(cart_frame, text="Clear All", command=self.clear_all, bg="gray", fg="white").place(x=10, y=340, width=120, height=32)

        bill_frame = LabelFrame(self.root, text="Bill", font=("goudy old style", 14, "bold"), bg="white")
        bill_frame.place(x=910, y=110, width=430, height=550)
        self.txt_bill_area = Text(bill_frame, bg="lightyellow")
        self.txt_bill_area.place(x=10, y=10, width=410, height=430)
        self.lbl_amnt = Label(bill_frame, text="Bill Amount\n[0.00]", bg="#3f51b5", fg="white", font=("times new roman", 12, "bold"))
        self.lbl_amnt.place(x=10, y=450, width=130, height=45)
        self.lbl_discount = Label(bill_frame, text=f"Discount\n[{DISCOUNT_PERCENT}%]", bg="#8bc34a", fg="white", font=("times new roman", 12, "bold"))
        self.lbl_discount.place(x=150, y=450, width=130, height=45)
        self.lbl_net_pay = Label(bill_frame, text="Net Pay\n[0.00]", bg="#607d8b", fg="white", font=("times new roman", 12, "bold"))
        self.lbl_net_pay.place(x=290, y=450, width=130, height=45)
        Button(bill_frame, text="Generate Bill", command=self.generate_bill, bg="#009688", fg="white").place(x=10, y=505, width=150, height=32)
        Button(bill_frame, text="Print", command=self.print_bill, bg="lightgreen", fg="white").place(x=170, y=505, width=120, height=32)
        Button(bill_frame, text="Clear Bill", command=lambda: self.txt_bill_area.delete("1.0", END), bg="lightgray").place(x=300, y=505, width=120, height=32)

    # ---------------------- DB helpers ----------------------
    def _run_query(self, query, params=(), *, fetchall=False, fetchone=False):
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute(query, params)
            if fetchall:
                return cur.fetchall()
            if fetchone:
                return cur.fetchone()
            con.commit()
            return None

    def _load_lookup_data(self):
        categories = ["All"] + [row[0] for row in self._run_query("select name from category order by name", fetchall=True)]
        employees = ["Select"] + [row[0] for row in self._run_query("select name from employee order by name", fetchall=True)]
        self.cmb_category.config(values=categories)
        self.cmb_employee.config(values=employees)

        customers = self._run_query("select cid,name,contact from customer order by name", fetchall=True)
        self.customer_map = {}
        customer_values = ["Select"]
        for cid, name, contact in customers:
            display = f"{name} | {contact}"
            self.customer_map[display] = (cid, name, contact)
            customer_values.append(display)
        self.cmb_customer.config(values=customer_values)

    # ---------------------- product list/cart ----------------------
    def show_products(self):
        query = "select pid,Category,Supplier,name,price,qty,COALESCE(employee,'') from product where status='Active'"
        params = []
        if self.var_category.get() and self.var_category.get() != "All":
            query += " and Category=?"
            params.append(self.var_category.get())
        if self.var_search.get().strip():
            query += " and name LIKE ?"
            params.append(f"%{self.var_search.get().strip()}%")
        query += " order by name"

        rows = self._run_query(query, tuple(params), fetchall=True)
        self.product_Table.delete(*self.product_Table.get_children())
        for row in rows:
            self.product_Table.insert("", END, values=row)

    def show(self):
        self.var_search.set("")
        self.var_category.set("All")
        self.show_products()

    def search(self):
        self.show_products()

    def get_data(self, _event):
        row = self.product_Table.item(self.product_Table.focus()).get("values", [])
        if not row:
            return
        self.var_pid.set(str(row[0]))
        self.var_pname.set(row[3])
        self.var_price.set(str(row[4]))
        self.var_stock.set(str(row[5]))
        self.var_selected_category.set(row[1])
        self.var_selected_supplier.set(row[2])
        self.var_qty.set("1")
        self.lbl_instock.config(text=f"In Stock [{row[5]}]")
        self.lbl_category.config(text=f"Category [{row[1]}]")
        if self.var_employee.get() == "Select" and row[6]:
            if row[6] in self.cmb_employee.cget("values"):
                self.var_employee.set(row[6])

    def add_update_cart(self):
        if not self.var_pid.get():
            messagebox.showerror("Error", "Please select product from list", parent=self.root)
            return
        try:
            qty = int(self.var_qty.get())
            stock = int(self.var_stock.get())
            price = float(self.var_price.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity/price", parent=self.root)
            return
        if qty < 0 or qty > stock:
            messagebox.showerror("Error", "Invalid quantity", parent=self.root)
            return

        pid = self.var_pid.get()
        if qty == 0:
            self.cart_items.pop(pid, None)
        else:
            self.cart_items[pid] = {
                "pid": pid,
                "name": self.var_pname.get(),
                "price": price,
                "qty": qty,
                "stock": stock,
                "category": self.var_selected_category.get(),
                "supplier": self.var_selected_supplier.get(),
            }
        self.show_cart()
        self.bill_update()

    def show_cart(self):
        self.CartTable.delete(*self.CartTable.get_children())
        for item in self.cart_items.values():
            self.CartTable.insert("", END, values=(item["pid"], item["name"], f"{item['price']:.2f}", item["qty"], item["category"]))

    def get_data_cart(self, _event):
        row = self.CartTable.item(self.CartTable.focus()).get("values", [])
        if not row:
            return
        self.var_pid.set(str(row[0]))
        self.var_pname.set(row[1])
        self.var_price.set(str(row[2]))
        self.var_qty.set(str(row[3]))
        self.var_selected_category.set(row[4])
        cart_item = self.cart_items.get(str(row[0]))
        if cart_item:
            self.var_stock.set(str(cart_item["stock"]))
            self.var_selected_supplier.set(cart_item.get("supplier", ""))
            self.lbl_instock.config(text=f"In Stock [{cart_item['stock']}]")
        self.lbl_category.config(text=f"Category [{row[4]}]")

    def clear_cart(self):
        self.var_pid.set("")
        self.var_pname.set("")
        self.var_price.set("")
        self.var_stock.set("")
        self.var_qty.set("1")
        self.var_selected_category.set("")
        self.var_selected_supplier.set("")
        self.lbl_instock.config(text="In Stock")
        self.lbl_category.config(text="Category")

    def clear_all(self):
        self.cart_items.clear()
        self.show_cart()
        self.bill_update()
        self.clear_cart()
        self.var_customer_select.set("Select")
        self.var_cname.set("")
        self.var_contact.set("")
        self.var_employee.set("Select")
        self.txt_bill_area.delete("1.0", END)
        self.chk_print = 0
        self.show_products()

    # ---------------------- billing ----------------------
    def bill_update(self):
        self.bill_amnt = sum(item["price"] * item["qty"] for item in self.cart_items.values())
        self.discount = (self.bill_amnt * DISCOUNT_PERCENT) / 100
        self.net_pay = self.bill_amnt - self.discount
        self.lbl_amnt.config(text=f"Bill Amount\n[{self.bill_amnt:.2f}]")
        self.lbl_net_pay.config(text=f"Net Pay\n[{self.net_pay:.2f}]")
        self.cartTitle.config(text=f"Total Products: [{len(self.cart_items)}]")

    def on_customer_select(self, _event):
        customer = self.customer_map.get(self.var_customer_select.get())
        if customer:
            self.var_cname.set(customer[1])
            self.var_contact.set(customer[2])

    def _get_or_create_customer(self, cursor, name, contact):
        cursor.execute("select cid from customer where name=? and contact=?", (name, contact))
        row = cursor.fetchone()
        if row:
            return row[0], False
        cursor.execute("insert into customer(name,contact) values(?,?)", (name, contact))
        return cursor.lastrowid, True

    def generate_bill(self):
        cname = self.var_cname.get().strip()
        contact = self.var_contact.get().strip()
        employee = self.var_employee.get().strip()
        if not cname or not contact:
            messagebox.showerror("Error", "Customer details are required", parent=self.root)
            return
        if employee in ("", "Select"):
            messagebox.showerror("Error", "Select employee for this bill", parent=self.root)
            return
        if not self.cart_items:
            messagebox.showerror("Error", "Please add products to cart", parent=self.root)
            return

        invoice = str(int(time.strftime("%H%M%S")) + int(time.strftime("%d%m%Y")))
        bill_date = time.strftime("%d/%m/%Y")
        bill_time = time.strftime("%H:%M:%S")
        bill_file = f"{invoice}.txt"
        bill_path = os.path.join(BILL_DIR, bill_file)

        lines = [
            "\t\tXYZ-Inventory",
            "\t Phone No. 9899459288 , Delhi-110053",
            "=" * 46,
            f" Customer Name: {cname}",
            f" Ph. no.: {contact}",
            f" Employee: {employee}",
            f" Bill No. {invoice}\t\tDate: {bill_date}",
            "=" * 46,
            " Product Name\t\t\tQTY\tPrice",
            "=" * 46,
        ]

        try:
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                customer_id, customer_added = self._get_or_create_customer(cur, cname, contact)
                for item in self.cart_items.values():
                    line_total = item["price"] * item["qty"]
                    lines.append(f" {item['name']}\t\t\t{item['qty']}\tRs.{line_total:.2f}")
                    remaining = item["stock"] - item["qty"]
                    status = "Inactive" if remaining <= 0 else "Active"
                    cur.execute("update product set qty=?,status=? where pid=?", (str(remaining), status, item["pid"]))
                    cur.execute(
                        "insert into sales_history(invoice,bill_file,customer_id,customer_name,customer_contact,employee,supplier,product_id,product_name,category,quantity,unit_price,line_total,bill_amount,discount,net_pay,bill_date,bill_time) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            invoice,
                            bill_file,
                            customer_id,
                            cname,
                            contact,
                            employee,
                            item.get("supplier", ""),
                            int(item["pid"]),
                            item["name"],
                            item["category"],
                            item["qty"],
                            item["price"],
                            line_total,
                            self.bill_amnt,
                            self.discount,
                            self.net_pay,
                            bill_date,
                            bill_time,
                        ),
                    )
                con.commit()

            lines += [
                "=" * 46,
                f" Bill Amount\t\t\t\tRs.{self.bill_amnt:.2f}",
                f" Discount\t\t\t\tRs.{self.discount:.2f}",
                f" Net Pay\t\t\t\tRs.{self.net_pay:.2f}",
                "=" * 46,
                "",
            ]
            bill_text = "\n".join(lines)
            with open(bill_path, "w", encoding="utf-8") as fp:
                fp.write(bill_text)

            self.chk_print = 1
            self.txt_bill_area.delete("1.0", END)
            self.txt_bill_area.insert("1.0", bill_text)
            self.show_products()
            if customer_added:
                self._load_lookup_data()
                key = f"{cname} | {contact}"
                if key in self.customer_map:
                    self.var_customer_select.set(key)
            messagebox.showinfo("Saved", "Bill has been generated", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)

    def print_bill(self):
        if self.chk_print != 1:
            messagebox.showinfo("Print", "Please generate bill to print the receipt", parent=self.root)
            return
        try:
            messagebox.showinfo("Print", "Please wait while printing", parent=self.root)
            new_file = tempfile.mktemp(".txt")
            with open(new_file, "w", encoding="utf-8") as fp:
                fp.write(self.txt_bill_area.get("1.0", END))
            os.startfile(new_file, "print")
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)

    def update_date_time(self):
        time_ = time.strftime("%I:%M:%S")
        date_ = time.strftime("%d-%m-%Y")
        self.lbl_clock.config(text=f"Welcome to Inventory Management System\t\t Date: {date_}\t\t Time: {time_}")
        self.root.after(200, self.update_date_time)


if __name__ == "__main__":
    root = Tk()
    obj = billClass(root)
    root.mainloop()
