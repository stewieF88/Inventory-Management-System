from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3

from create_db import create_db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BILL_DIR = os.path.join(BASE_DIR, "bill")
DB_PATH = os.path.join(BASE_DIR, "ims.db")
INVOICE_FILTER_COLUMN_MAP = {
    "Employee": "employee",
    "Product": "product_name",
    "Category": "category",
}
TRANSACTION_FILTER_COLUMN_MAP = {
    "Employee": "employee",
    "Product": "product",
    "Category": "category",
}

os.makedirs(BILL_DIR, exist_ok=True)


class salesClass:
    def __init__(self, root):
        create_db()

        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        self.invoice_list = []
        self.transaction_meta = {}
        self.var_invoice = StringVar()
        self.var_filter_by = StringVar(value="Select")
        self.var_filter_txt = StringVar()

        Label(
            self.root,
            text="View Customer Bills",
            font=("goudy old style", 30),
            bg="#184a45",
            fg="white",
            bd=3,
            relief=RIDGE,
        ).pack(side=TOP, fill=X, padx=10, pady=20)

        # Invoice search
        Label(self.root, text="Invoice No.", font=("times new roman", 13), bg="white").place(x=30, y=92)
        Entry(self.root, textvariable=self.var_invoice, font=("times new roman", 13), bg="lightyellow").place(x=120, y=92, width=140, height=24)
        Button(self.root, text="Search", command=self.search, font=("times new roman", 12, "bold"), bg="#2196f3", fg="white").place(x=270, y=92, width=90, height=24)
        Button(self.root, text="Delete Bill", command=self.delete_bill, font=("times new roman", 12, "bold"), bg="#f44336", fg="white").place(x=370, y=92, width=110, height=24)
        Button(self.root, text="Clear", command=self.clear, font=("times new roman", 12, "bold"), bg="lightgray").place(x=490, y=92, width=80, height=24)

        # History filter
        Label(self.root, text="Filter By", font=("times new roman", 13), bg="white").place(x=590, y=92)
        self.cmb_filter_by = ttk.Combobox(
            self.root,
            textvariable=self.var_filter_by,
            values=("Select", "Employee", "Product", "Category"),
            state="readonly",
            justify=CENTER,
            font=("times new roman", 11),
        )
        self.cmb_filter_by.place(x=660, y=92, width=120, height=24)
        self.cmb_filter_by.current(0)
        Entry(self.root, textvariable=self.var_filter_txt, font=("times new roman", 13), bg="lightyellow").place(x=790, y=92, width=170, height=24)
        Button(self.root, text="Apply", command=self.apply_filter, font=("times new roman", 12, "bold"), bg="#4caf50", fg="white").place(x=970, y=92, width=80, height=24)

        # Bill list
        list_frame = Frame(self.root, bd=3, relief=RIDGE)
        list_frame.place(x=30, y=130, width=220, height=340)
        list_scroll = Scrollbar(list_frame, orient=VERTICAL)
        self.Sales_List = Listbox(list_frame, font=("goudy old style", 14), bg="white", yscrollcommand=list_scroll.set)
        list_scroll.pack(side=RIGHT, fill=Y)
        list_scroll.config(command=self.Sales_List.yview)
        self.Sales_List.pack(fill=BOTH, expand=1)
        self.Sales_List.bind("<ButtonRelease-1>", self.get_data)

        # Bill area
        bill_frame = Frame(self.root, bd=3, relief=RIDGE)
        bill_frame.place(x=270, y=130, width=430, height=340)
        Label(bill_frame, text="Customer Bill Area", font=("goudy old style", 20), bg="orange").pack(side=TOP, fill=X)
        bill_scroll = Scrollbar(bill_frame, orient=VERTICAL)
        self.bill_area = Text(bill_frame, bg="lightyellow", yscrollcommand=bill_scroll.set)
        bill_scroll.pack(side=RIGHT, fill=Y)
        bill_scroll.config(command=self.bill_area.yview)
        self.bill_area.pack(fill=BOTH, expand=1)

        # Transaction history table (right side)
        history_frame = Frame(self.root, bd=3, relief=RIDGE)
        history_frame.place(x=710, y=130, width=360, height=340)
        history_header = Frame(history_frame, bg="#009688")
        history_header.place(x=2, y=2, width=352, height=30)
        Label(history_header, text="Transaction History", font=("goudy old style", 16), bg="#009688", fg="white").pack(side=LEFT, padx=6)
        Button(
            history_header,
            text="Delete Tx",
            command=self.delete_transaction,
            font=("times new roman", 10, "bold"),
            bg="#f44336",
            fg="white",
        ).pack(side=RIGHT, padx=4, pady=2)

        history_inner = Frame(history_frame, bd=1, relief=RIDGE)
        history_inner.place(x=2, y=35, width=352, height=300)
        history_scrolly = Scrollbar(history_inner, orient=VERTICAL)
        history_scrollx = Scrollbar(history_inner, orient=HORIZONTAL)
        self.HistoryTable = ttk.Treeview(
            history_inner,
            columns=("id", "invoice", "employee", "supplier", "product", "category", "qty", "amount"),
            yscrollcommand=history_scrolly.set,
            xscrollcommand=history_scrollx.set,
        )
        history_scrolly.pack(side=RIGHT, fill=Y)
        history_scrollx.pack(side=BOTTOM, fill=X)
        history_scrolly.config(command=self.HistoryTable.yview)
        history_scrollx.config(command=self.HistoryTable.xview)
        self.HistoryTable.heading("id", text="ID")
        self.HistoryTable.heading("invoice", text="Invoice")
        self.HistoryTable.heading("employee", text="Employee")
        self.HistoryTable.heading("supplier", text="Supplier")
        self.HistoryTable.heading("product", text="Product")
        self.HistoryTable.heading("category", text="Category")
        self.HistoryTable.heading("qty", text="Qty")
        self.HistoryTable.heading("amount", text="Amount")
        self.HistoryTable["show"] = "headings"
        self.HistoryTable.column("id", width=35)
        self.HistoryTable.column("invoice", width=75)
        self.HistoryTable.column("employee", width=95)
        self.HistoryTable.column("supplier", width=95)
        self.HistoryTable.column("product", width=90)
        self.HistoryTable.column("category", width=80)
        self.HistoryTable.column("qty", width=45)
        self.HistoryTable.column("amount", width=70)
        self.HistoryTable.pack(fill=BOTH, expand=1)

        self.show()

    # -------------------------------------------------------
    def _run_query(self, query, params=(), *, fetchall=False):
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute(query, params)
            if fetchall:
                return cur.fetchall()
            con.commit()
            return None

    def _history_invoices(self, filter_by=None, filter_text=""):
        if filter_by and filter_text:
            column_name = INVOICE_FILTER_COLUMN_MAP[filter_by]
            rows = self._run_query(
                f"select distinct invoice from sales_history where {column_name} LIKE ? order by id desc",
                (f"%{filter_text}%",),
                fetchall=True,
            )
        else:
            rows = self._run_query("select distinct invoice from sales_history order by id desc", fetchall=True)
        return [str(row[0]) for row in rows]

    def _populate_invoices(self, invoices):
        self.invoice_list = invoices
        self.Sales_List.delete(0, END)
        for invoice in invoices:
            self.Sales_List.insert(END, f"{invoice}.txt")

    def _display_invoice(self, invoice):
        file_path = os.path.join(BILL_DIR, f"{invoice}.txt")
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Bill file not found", parent=self.root)
            return

        self.bill_area.delete("1.0", END)
        with open(file_path, "r", encoding="utf-8") as fp:
            self.bill_area.insert(END, fp.read())

    def _load_invoices(self, filter_by=None, filter_text=""):
        history_invoices = self._history_invoices(filter_by, filter_text)

        # Keep compatibility with old bill files without history rows.
        if filter_by is None:
            file_invoices = []
            for file_name in os.listdir(BILL_DIR):
                if file_name.endswith(".txt"):
                    file_invoices.append(os.path.splitext(file_name)[0])
            history_invoices = sorted(set(history_invoices).union(file_invoices), reverse=True)

        self._populate_invoices(history_invoices)

    def _load_transactions(self, filter_by=None, filter_text=""):
        sales_query = (
            "select sh.id as tx_id,sh.invoice as reference,COALESCE(sh.employee,'') as employee,"
            "COALESCE(sh.supplier,COALESCE(p.Supplier,'')) as supplier,COALESCE(sh.product_name,'') as product,"
            "COALESCE(sh.category,'') as category,-ABS(COALESCE(sh.quantity,0)) as qty,"
            "-ABS(COALESCE(sh.line_total,0)) as amount,COALESCE(sh.bill_date,'') as tx_date,"
            "COALESCE(sh.bill_time,'') as tx_time,'SALE' as tx_source "
            "from sales_history sh left join product p on p.pid = sh.product_id"
        )
        stock_query = (
            "select ih.id,COALESCE(ih.reference,'STOCK-IN'),COALESCE(ih.employee,''),"
            "COALESCE(ih.supplier,''),COALESCE(ih.product_name,''),COALESCE(ih.category,''),"
            "COALESCE(ih.quantity,0),COALESCE(ih.line_total,0),COALESCE(ih.trans_date,''),COALESCE(ih.trans_time,''),'STOCK' "
            "from inventory_history ih"
        )
        query = (
            "select tx_id,reference,employee,supplier,product,category,qty,amount,tx_date,tx_time,tx_source "
            f"from ({sales_query} union all {stock_query}) tx"
        )
        params = []
        if filter_by and filter_text:
            column_name = TRANSACTION_FILTER_COLUMN_MAP[filter_by]
            query += f" where tx.{column_name} LIKE ?"
            params.append(f"%{filter_text}%")
        query += (
            " order by "
            "(substr(tx.tx_date,7,4)||substr(tx.tx_date,4,2)||substr(tx.tx_date,1,2)) desc,"
            "replace(tx.tx_time,':','') desc,tx.tx_id desc"
        )

        rows = self._run_query(query, tuple(params), fetchall=True)
        self.HistoryTable.delete(*self.HistoryTable.get_children())
        self.transaction_meta = {}
        for row in rows:
            qty_value = int(row[6]) if row[6] is not None else 0
            amount_value = float(row[7]) if row[7] is not None else 0.0
            item_id = self.HistoryTable.insert(
                "",
                END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    f"{qty_value:+d}",
                    f"{amount_value:+.2f}",
                ),
            )
            self.transaction_meta[item_id] = {
                "id": int(row[0]),
                "reference": str(row[1]),
                "source": row[10],
            }

    def _delete_invoice_data(self, invoice):
        file_path = os.path.join(BILL_DIR, f"{invoice}.txt")
        file_deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True

        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute("delete from sales_history where invoice=?", (invoice,))
            history_deleted_count = cur.rowcount
            con.commit()
        return file_deleted, history_deleted_count

    def _refresh_current_view(self):
        filter_by = self.var_filter_by.get().strip()
        filter_txt = self.var_filter_txt.get().strip()
        if filter_by != "Select" and filter_txt:
            self._load_invoices(filter_by, filter_txt)
            self._load_transactions(filter_by, filter_txt)
        else:
            self.show()

    def delete_transaction(self):
        selection = self.HistoryTable.focus()
        if not selection:
            messagebox.showerror("Error", "Select transaction from the table", parent=self.root)
            return

        transaction = self.transaction_meta.get(selection)
        if not transaction:
            messagebox.showerror("Error", "Unable to identify selected transaction", parent=self.root)
            return

        try:
            if transaction["source"] == "SALE":
                invoice = transaction["reference"]
                if not messagebox.askyesno(
                    "Confirm",
                    f"Delete sales transaction for invoice {invoice}?\nThis removes all rows of that invoice.",
                    parent=self.root,
                ):
                    return

                file_deleted, history_deleted_count = self._delete_invoice_data(invoice)
                if not file_deleted and history_deleted_count == 0:
                    messagebox.showerror("Error", "Invoice not found", parent=self.root)
                    return

                self.bill_area.delete("1.0", END)
                self.var_invoice.set("")
                messagebox.showinfo("Success", "Sales transaction deleted successfully", parent=self.root)
            elif transaction["source"] == "STOCK":
                if not messagebox.askyesno("Confirm", "Delete selected stock transaction?", parent=self.root):
                    return

                with sqlite3.connect(DB_PATH) as con:
                    cur = con.cursor()
                    cur.execute("delete from inventory_history where id=?", (transaction["id"],))
                    deleted_count = cur.rowcount
                    con.commit()
                if deleted_count == 0:
                    messagebox.showerror("Error", "Transaction not found", parent=self.root)
                    return

                messagebox.showinfo("Success", "Stock transaction deleted successfully", parent=self.root)
            else:
                messagebox.showerror("Error", "Unknown transaction type", parent=self.root)
                return

            self._refresh_current_view()
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)

    def show(self):
        self._load_invoices()
        self._load_transactions()

    def get_data(self, _event):
        selection = self.Sales_List.curselection()
        if not selection:
            return
        file_name = self.Sales_List.get(selection)
        invoice = os.path.splitext(file_name)[0]
        self.var_invoice.set(invoice)
        self._display_invoice(invoice)

    def search(self):
        invoice = self.var_invoice.get().strip()
        if not invoice:
            messagebox.showerror("Error", "Invoice no. should be required", parent=self.root)
            return
        if invoice not in self.invoice_list and not os.path.exists(os.path.join(BILL_DIR, f"{invoice}.txt")):
            messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
            return
        self._display_invoice(invoice)

    def apply_filter(self):
        filter_by = self.var_filter_by.get().strip()
        filter_txt = self.var_filter_txt.get().strip()
        if filter_by == "Select":
            messagebox.showerror("Error", "Select filter type", parent=self.root)
            return
        if not filter_txt:
            messagebox.showerror("Error", "Filter text is required", parent=self.root)
            return

        self._load_invoices(filter_by, filter_txt)
        self._load_transactions(filter_by, filter_txt)
        if not self.invoice_list:
            messagebox.showinfo("Info", "No matching history found", parent=self.root)

    def delete_bill(self):
        invoice = self.var_invoice.get().strip()
        if not invoice:
            selection = self.Sales_List.curselection()
            if selection:
                invoice = os.path.splitext(self.Sales_List.get(selection))[0]

        if not invoice:
            messagebox.showerror("Error", "Select or enter invoice to delete", parent=self.root)
            return

        if not messagebox.askyesno("Confirm", f"Delete bill {invoice}?", parent=self.root):
            return

        try:
            file_deleted, history_deleted_count = self._delete_invoice_data(invoice)

            if not file_deleted and history_deleted_count == 0:
                messagebox.showerror("Error", "Invoice not found", parent=self.root)
                return

            messagebox.showinfo("Success", "Bill deleted successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)

    def clear(self):
        self.var_invoice.set("")
        self.var_filter_by.set("Select")
        self.var_filter_txt.set("")
        self.bill_area.delete("1.0", END)
        self.show()


if __name__ == "__main__":
    root = Tk()
    obj = salesClass(root)
    root.mainloop()
