from tkinter import *
from tkinter import ttk, messagebox
import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")
SEARCH_COLUMN_MAP = {
    "Email": "email",
    "Name": "name",
    "Contact": "contact",
}


class employeeClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ------------ all variables --------------
        self.var_searchby = StringVar(value="Select")
        self.var_searchtxt = StringVar()
        self.var_emp_id = StringVar()
        self.var_gender = StringVar(value="Select")
        self.var_contact = StringVar()
        self.var_name = StringVar()
        self.var_dob = StringVar()
        self.var_doj = StringVar()
        self.var_email = StringVar()
        self.var_pass = StringVar()
        self.var_utype = StringVar(value="Admin")
        self.var_salary = StringVar()

        # ---------- Search Frame -------------
        search_frame = LabelFrame(
            self.root,
            text="Search Employee",
            font=("goudy old style", 12, "bold"),
            bd=2,
            relief=RIDGE,
            bg="white",
        )
        search_frame.place(x=250, y=20, width=600, height=70)

        cmb_search = ttk.Combobox(
            search_frame,
            textvariable=self.var_searchby,
            values=("Select", "Email", "Name", "Contact"),
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
            command=self.search,
            text="Search",
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=410, y=9, width=150, height=30)

        # -------------- title ---------------
        Label(
            self.root,
            text="Employee Details",
            font=("goudy old style", 15),
            bg="#0f4d7d",
            fg="white",
        ).place(x=50, y=100, width=1000)

        # -------------- content ---------------
        Label(self.root, text="Emp ID", font=("goudy old style", 15), bg="white").place(x=50, y=150)
        Label(self.root, text="Gender", font=("goudy old style", 15), bg="white").place(x=350, y=150)
        Label(self.root, text="Contact", font=("goudy old style", 15), bg="white").place(x=750, y=150)

        Entry(self.root, textvariable=self.var_emp_id, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=150, width=180
        )
        cmb_gender = ttk.Combobox(
            self.root,
            textvariable=self.var_gender,
            values=("Select", "Male", "Female", "Other"),
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        cmb_gender.place(x=500, y=150, width=180)
        cmb_gender.current(0)
        Entry(self.root, textvariable=self.var_contact, font=("goudy old style", 15), bg="lightyellow").place(
            x=850, y=150, width=180
        )

        Label(self.root, text="Name", font=("goudy old style", 15), bg="white").place(x=50, y=190)
        Label(self.root, text="D.O.B.", font=("goudy old style", 15), bg="white").place(x=350, y=190)
        Label(self.root, text="D.O.J.", font=("goudy old style", 15), bg="white").place(x=750, y=190)

        Entry(self.root, textvariable=self.var_name, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=190, width=180
        )
        Entry(self.root, textvariable=self.var_dob, font=("goudy old style", 15), bg="lightyellow").place(
            x=500, y=190, width=180
        )
        Entry(self.root, textvariable=self.var_doj, font=("goudy old style", 15), bg="lightyellow").place(
            x=850, y=190, width=180
        )

        Label(self.root, text="Email", font=("goudy old style", 15), bg="white").place(x=50, y=230)
        Label(self.root, text="Password", font=("goudy old style", 15), bg="white").place(x=350, y=230)
        Label(self.root, text="User Type", font=("goudy old style", 15), bg="white").place(x=750, y=230)

        Entry(self.root, textvariable=self.var_email, font=("goudy old style", 15), bg="lightyellow").place(
            x=150, y=230, width=180
        )
        Entry(self.root, textvariable=self.var_pass, font=("goudy old style", 15), bg="lightyellow").place(
            x=500, y=230, width=180
        )
        cmb_utype = ttk.Combobox(
            self.root,
            textvariable=self.var_utype,
            values=("Admin", "Employee"),
            state="readonly",
            justify=CENTER,
            font=("goudy old style", 15),
        )
        cmb_utype.place(x=850, y=230, width=180)
        cmb_utype.current(0)

        Label(self.root, text="Address", font=("goudy old style", 15), bg="white").place(x=50, y=270)
        Label(self.root, text="Salary", font=("goudy old style", 15), bg="white").place(x=500, y=270)

        self.txt_address = Text(self.root, font=("goudy old style", 15), bg="lightyellow")
        self.txt_address.place(x=150, y=270, width=300, height=60)
        Entry(self.root, textvariable=self.var_salary, font=("goudy old style", 15), bg="lightyellow").place(
            x=600, y=270, width=180
        )

        # -------------- buttons -----------------
        Button(
            self.root,
            text="Save",
            command=self.add,
            font=("goudy old style", 15),
            bg="#2196f3",
            fg="white",
            cursor="hand2",
        ).place(x=500, y=305, width=110, height=28)
        Button(
            self.root,
            text="Update",
            command=self.update,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=620, y=305, width=110, height=28)
        Button(
            self.root,
            text="Delete",
            command=self.delete,
            font=("goudy old style", 15),
            bg="#f44336",
            fg="white",
            cursor="hand2",
        ).place(x=740, y=305, width=110, height=28)
        Button(
            self.root,
            text="Clear",
            command=self.clear,
            font=("goudy old style", 15),
            bg="#607d8b",
            fg="white",
            cursor="hand2",
        ).place(x=860, y=305, width=110, height=28)

        # ------------ employee details -------------
        emp_frame = Frame(self.root, bd=3, relief=RIDGE)
        emp_frame.place(x=0, y=350, relwidth=1, height=150)

        scrolly = Scrollbar(emp_frame, orient=VERTICAL)
        scrollx = Scrollbar(emp_frame, orient=HORIZONTAL)

        self.EmployeeTable = ttk.Treeview(
            emp_frame,
            columns=("eid", "name", "email", "gender", "contact", "dob", "doj", "pass", "utype", "address", "salary"),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set,
        )
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.EmployeeTable.xview)
        scrolly.config(command=self.EmployeeTable.yview)
        self.EmployeeTable.heading("eid", text="EMP ID")
        self.EmployeeTable.heading("name", text="Name")
        self.EmployeeTable.heading("email", text="Email")
        self.EmployeeTable.heading("gender", text="Gender")
        self.EmployeeTable.heading("contact", text="Contact")
        self.EmployeeTable.heading("dob", text="D.O.B")
        self.EmployeeTable.heading("doj", text="D.O.J")
        self.EmployeeTable.heading("pass", text="Password")
        self.EmployeeTable.heading("utype", text="User Type")
        self.EmployeeTable.heading("address", text="Address")
        self.EmployeeTable.heading("salary", text="Salary")
        self.EmployeeTable["show"] = "headings"
        self.EmployeeTable.column("eid", width=90)
        self.EmployeeTable.column("name", width=100)
        self.EmployeeTable.column("email", width=100)
        self.EmployeeTable.column("gender", width=100)
        self.EmployeeTable.column("contact", width=100)
        self.EmployeeTable.column("dob", width=100)
        self.EmployeeTable.column("doj", width=100)
        self.EmployeeTable.column("pass", width=100)
        self.EmployeeTable.column("utype", width=100)
        self.EmployeeTable.column("address", width=100)
        self.EmployeeTable.column("salary", width=100)

        self.EmployeeTable.pack(fill=BOTH, expand=1)
        self.EmployeeTable.bind("<ButtonRelease-1>", self.get_data)
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

    def _populate_employee_table(self, rows):
        self.EmployeeTable.delete(*self.EmployeeTable.get_children())
        for row in rows:
            self.EmployeeTable.insert("", END, values=row)

    def _selected_employee_row(self):
        focused_item = self.EmployeeTable.focus()
        if not focused_item:
            return None
        row = self.EmployeeTable.item(focused_item).get("values", [])
        return row if row else None

    def _employee_values(self):
        return (
            self.var_name.get().strip(),
            self.var_email.get().strip(),
            self.var_gender.get(),
            self.var_contact.get().strip(),
            self.var_dob.get().strip(),
            self.var_doj.get().strip(),
            self.var_pass.get(),
            self.var_utype.get(),
            self.txt_address.get("1.0", END).strip(),
            self.var_salary.get().strip(),
        )

    def add(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showerror("Error", "Employee ID must be required", parent=self.root)
            return

        try:
            if self._run_query("select 1 from employee where eid=?", (emp_id,), fetchone=True):
                messagebox.showerror("Error", "This Employee ID is already assigned", parent=self.root)
                return

            self._run_query(
                "insert into employee(eid,name,email,gender,contact,dob,doj,pass,utype,address,salary) values(?,?,?,?,?,?,?,?,?,?,?)",
                (emp_id,) + self._employee_values(),
            )
            messagebox.showinfo("Success", "Employee Added Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def show(self):
        try:
            rows = self._run_query("select * from employee", fetchall=True)
            self._populate_employee_table(rows)
        except Exception as ex:
            self._handle_error(ex)

    def get_data(self, _event):
        row = self._selected_employee_row()
        if not row:
            return

        self.var_emp_id.set(row[0])
        self.var_name.set(row[1])
        self.var_email.set(row[2])
        self.var_gender.set(row[3])
        self.var_contact.set(row[4])
        self.var_dob.set(row[5])
        self.var_doj.set(row[6])
        self.var_pass.set(row[7])
        self.var_utype.set(row[8])
        self.txt_address.delete("1.0", END)
        self.txt_address.insert(END, row[9])
        self.var_salary.set(row[10])

    def update(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showerror("Error", "Employee ID must be required", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from employee where eid=?", (emp_id,), fetchone=True):
                messagebox.showerror("Error", "Invalid Employee ID", parent=self.root)
                return

            self._run_query(
                "update employee set name=?,email=?,gender=?,contact=?,dob=?,doj=?,pass=?,utype=?,address=?,salary=? where eid=?",
                self._employee_values() + (emp_id,),
            )
            messagebox.showinfo("Success", "Employee Updated Successfully", parent=self.root)
            self.show()
        except Exception as ex:
            self._handle_error(ex)

    def delete(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showerror("Error", "Employee ID must be required", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from employee where eid=?", (emp_id,), fetchone=True):
                messagebox.showerror("Error", "Invalid Employee ID", parent=self.root)
                return

            if not messagebox.askyesno("Confirm", "Do you really want to delete?", parent=self.root):
                return

            self._run_query("delete from employee where eid=?", (emp_id,))
            messagebox.showinfo("Delete", "Employee Deleted Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def clear(self):
        self.var_emp_id.set("")
        self.var_name.set("")
        self.var_email.set("")
        self.var_gender.set("Select")
        self.var_contact.set("")
        self.var_dob.set("")
        self.var_doj.set("")
        self.var_pass.set("")
        self.var_utype.set("Admin")
        self.var_salary.set("")
        self.var_searchby.set("Select")
        self.var_searchtxt.set("")
        self.txt_address.delete("1.0", END)
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
                f"select * from employee where {column_name} LIKE ?",
                (f"%{search_text}%",),
                fetchall=True,
            )
            if rows:
                self._populate_employee_table(rows)
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)
        except Exception as ex:
            self._handle_error(ex)


if __name__ == "__main__":
    root = Tk()
    obj = employeeClass(root)
    root.mainloop()
