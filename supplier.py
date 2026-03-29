from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")


class supplierClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ------------ all variables --------------
        self.var_searchtxt = StringVar()
        self.var_sup_invoice = StringVar()
        self.var_name = StringVar()
        self.var_contact = StringVar()

        # ---------- Search Frame -------------
        Label(self.root, text="Invoice No.", bg="white", font=("goudy old style", 15)).place(x=700, y=80)
        Entry(
            self.root,
            textvariable=self.var_searchtxt,
            font=("goudy old style", 15),
            bg="lightyellow",
        ).place(x=850, y=80, width=160)
        Button(
            self.root,
            command=self.search,
            text="Search",
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=980, y=79, width=100, height=28)

        # -------------- title ---------------
        Label(
            self.root,
            text="Supplier Details",
            font=("goudy old style", 20, "bold"),
            bg="#0f4d7d",
            fg="white",
        ).place(x=50, y=10, width=1000, height=40)

        # -------------- content ---------------
        Label(self.root, text="Invoice No.", font=("goudy old style", 15), bg="white").place(x=50, y=80)
        Entry(
            self.root,
            textvariable=self.var_sup_invoice,
            font=("goudy old style", 15),
            bg="lightyellow",
        ).place(x=180, y=80, width=180)

        Label(self.root, text="Name", font=("goudy old style", 15), bg="white").place(x=50, y=120)
        Entry(self.root, textvariable=self.var_name, font=("goudy old style", 15), bg="lightyellow").place(
            x=180, y=120, width=180
        )

        Label(self.root, text="Contact", font=("goudy old style", 15), bg="white").place(x=50, y=160)
        Entry(
            self.root,
            textvariable=self.var_contact,
            font=("goudy old style", 15),
            bg="lightyellow",
        ).place(x=180, y=160, width=180)

        Label(self.root, text="Description", font=("goudy old style", 15), bg="white").place(x=50, y=200)
        self.txt_desc = Text(self.root, font=("goudy old style", 15), bg="lightyellow")
        self.txt_desc.place(x=180, y=200, width=470, height=120)

        # -------------- buttons -----------------
        Button(
            self.root,
            text="Save",
            command=self.add,
            font=("goudy old style", 15),
            bg="#2196f3",
            fg="white",
            cursor="hand2",
        ).place(x=180, y=370, width=110, height=35)
        Button(
            self.root,
            text="Update",
            command=self.update,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=300, y=370, width=110, height=35)
        Button(
            self.root,
            text="Delete",
            command=self.delete,
            font=("goudy old style", 15),
            bg="#f44336",
            fg="white",
            cursor="hand2",
        ).place(x=420, y=370, width=110, height=35)
        Button(
            self.root,
            text="Clear",
            command=self.clear,
            font=("goudy old style", 15),
            bg="#607d8b",
            fg="white",
            cursor="hand2",
        ).place(x=540, y=370, width=110, height=35)

        # ------------ supplier details -------------
        sup_frame = Frame(self.root, bd=3, relief=RIDGE)
        sup_frame.place(x=700, y=120, width=380, height=350)

        scrolly = Scrollbar(sup_frame, orient=VERTICAL)
        scrollx = Scrollbar(sup_frame, orient=HORIZONTAL)

        self.SupplierTable = ttk.Treeview(
            sup_frame,
            columns=("invoice", "name", "contact", "desc"),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set,
        )
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.SupplierTable.xview)
        scrolly.config(command=self.SupplierTable.yview)
        self.SupplierTable.heading("invoice", text="Invoice")
        self.SupplierTable.heading("name", text="Name")
        self.SupplierTable.heading("contact", text="Contact")
        self.SupplierTable.heading("desc", text="Description")
        self.SupplierTable["show"] = "headings"
        self.SupplierTable.column("invoice", width=90)
        self.SupplierTable.column("name", width=100)
        self.SupplierTable.column("contact", width=100)
        self.SupplierTable.column("desc", width=100)

        self.SupplierTable.pack(fill=BOTH, expand=1)
        self.SupplierTable.bind("<ButtonRelease-1>", self.get_data)
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

    def _populate_supplier_table(self, rows):
        self.SupplierTable.delete(*self.SupplierTable.get_children())
        for row in rows:
            self.SupplierTable.insert("", END, values=row)

    def _selected_supplier_row(self):
        focused_item = self.SupplierTable.focus()
        if not focused_item:
            return None
        row = self.SupplierTable.item(focused_item).get("values", [])
        return row if row else None

    def _get_form_values(self):
        return (
            self.var_name.get().strip(),
            self.var_contact.get().strip(),
            self.txt_desc.get("1.0", END).strip(),
        )

    def add(self):
        invoice = self.var_sup_invoice.get().strip()
        if not invoice:
            messagebox.showerror("Error", "Invoice must be required", parent=self.root)
            return

        try:
            if self._run_query("select 1 from supplier where invoice=?", (invoice,), fetchone=True):
                messagebox.showerror("Error", "Invoice no. is already assigned", parent=self.root)
                return

            name, contact, description = self._get_form_values()
            self._run_query(
                "insert into supplier(invoice,name,contact,desc) values(?,?,?,?)",
                (invoice, name, contact, description),
            )
            messagebox.showinfo("Success", "Supplier Added Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def show(self):
        try:
            rows = self._run_query("select * from supplier", fetchall=True)
            self._populate_supplier_table(rows)
        except Exception as ex:
            self._handle_error(ex)

    def get_data(self, _event):
        row = self._selected_supplier_row()
        if not row:
            return

        self.var_sup_invoice.set(row[0])
        self.var_name.set(row[1])
        self.var_contact.set(row[2])
        self.txt_desc.delete("1.0", END)
        self.txt_desc.insert(END, row[3])

    def update(self):
        invoice = self.var_sup_invoice.get().strip()
        if not invoice:
            messagebox.showerror("Error", "Invoice must be required", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from supplier where invoice=?", (invoice,), fetchone=True):
                messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
                return

            name, contact, description = self._get_form_values()
            self._run_query(
                "update supplier set name=?,contact=?,desc=? where invoice=?",
                (name, contact, description, invoice),
            )
            messagebox.showinfo("Success", "Supplier Updated Successfully", parent=self.root)
            self.show()
        except Exception as ex:
            self._handle_error(ex)

    def delete(self):
        invoice = self.var_sup_invoice.get().strip()
        if not invoice:
            messagebox.showerror("Error", "Invoice No. must be required", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from supplier where invoice=?", (invoice,), fetchone=True):
                messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
                return

            if not messagebox.askyesno("Confirm", "Do you really want to delete?", parent=self.root):
                return

            self._run_query("delete from supplier where invoice=?", (invoice,))
            messagebox.showinfo("Delete", "Supplier Deleted Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def clear(self):
        self.var_sup_invoice.set("")
        self.var_name.set("")
        self.var_contact.set("")
        self.var_searchtxt.set("")
        self.txt_desc.delete("1.0", END)
        self.show()

    def search(self):
        invoice = self.var_searchtxt.get().strip()
        if not invoice:
            messagebox.showerror("Error", "Invoice No. should be required", parent=self.root)
            return

        try:
            row = self._run_query("select * from supplier where invoice=?", (invoice,), fetchone=True)
            if row:
                self._populate_supplier_table([row])
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)
        except Exception as ex:
            self._handle_error(ex)


if __name__ == "__main__":
    root = Tk()
    obj = supplierClass(root)
    root.mainloop()
