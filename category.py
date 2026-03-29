from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
DB_PATH = os.path.join(BASE_DIR, "ims.db")


class categoryClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ------------ variables -------------
        self.var_cat_id = StringVar()
        self.var_name = StringVar()

        Label(
            self.root,
            text="Manage Product Category",
            font=("goudy old style", 30),
            bg="#184a45",
            fg="white",
            bd=3,
            relief=RIDGE,
        ).pack(side=TOP, fill=X, padx=10, pady=20)

        Label(self.root, text="Enter Category Name", font=("goudy old style", 30), bg="white").place(x=50, y=100)
        Entry(self.root, textvariable=self.var_name, bg="lightyellow", font=("goudy old style", 18)).place(
            x=50, y=170, width=300
        )

        Button(
            self.root,
            text="ADD",
            command=self.add,
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2",
        ).place(x=360, y=170, width=150, height=30)
        Button(
            self.root,
            text="Delete",
            command=self.delete,
            font=("goudy old style", 15),
            bg="red",
            fg="white",
            cursor="hand2",
        ).place(x=520, y=170, width=150, height=30)

        # ------------ category details -------------
        cat_frame = Frame(self.root, bd=3, relief=RIDGE)
        cat_frame.place(x=700, y=100, width=380, height=100)

        scrolly = Scrollbar(cat_frame, orient=VERTICAL)
        scrollx = Scrollbar(cat_frame, orient=HORIZONTAL)

        self.CategoryTable = ttk.Treeview(
            cat_frame,
            columns=("cid", "name"),
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set,
        )
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.CategoryTable.xview)
        scrolly.config(command=self.CategoryTable.yview)
        self.CategoryTable.heading("cid", text="C ID")
        self.CategoryTable.heading("name", text="Name")
        self.CategoryTable["show"] = "headings"
        self.CategoryTable.column("cid", width=90)
        self.CategoryTable.column("name", width=100)

        self.CategoryTable.pack(fill=BOTH, expand=1)
        self.CategoryTable.bind("<ButtonRelease-1>", self.get_data)
        self.show()

        # ----------------- images ---------------------
        self.im1 = Image.open(os.path.join(IMAGE_DIR, "cat.jpg"))
        self.im1 = self.im1.resize((500, 250))
        self.im1 = ImageTk.PhotoImage(self.im1)
        self.lbl_im1 = Label(self.root, image=self.im1, bd=2, relief=RAISED)
        self.lbl_im1.place(x=50, y=220)

        self.im2 = Image.open(os.path.join(IMAGE_DIR, "category.jpg"))
        self.im2 = self.im2.resize((500, 250))
        self.im2 = ImageTk.PhotoImage(self.im2)
        self.lbl_im2 = Label(self.root, image=self.im2, bd=2, relief=RAISED)
        self.lbl_im2.place(x=580, y=220)

    # ----------------------------------------------------------------------------------
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

    def _populate_category_table(self, rows):
        self.CategoryTable.delete(*self.CategoryTable.get_children())
        for row in rows:
            self.CategoryTable.insert("", END, values=row)

    def _selected_category_row(self):
        focused_item = self.CategoryTable.focus()
        if not focused_item:
            return None
        row = self.CategoryTable.item(focused_item).get("values", [])
        return row if row else None

    def add(self):
        category_name = self.var_name.get().strip()
        if not category_name:
            messagebox.showerror("Error", "Category Name must be required", parent=self.root)
            return

        try:
            if self._run_query("select 1 from category where name=?", (category_name,), fetchone=True):
                messagebox.showerror("Error", "Category already present", parent=self.root)
                return

            self._run_query("insert into category(name) values(?)", (category_name,))
            messagebox.showinfo("Success", "Category Added Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)

    def show(self):
        try:
            rows = self._run_query("select * from category", fetchall=True)
            self._populate_category_table(rows)
        except Exception as ex:
            self._handle_error(ex)

    def clear(self):
        self.var_cat_id.set("")
        self.var_name.set("")
        self.show()

    def get_data(self, _event):
        row = self._selected_category_row()
        if not row:
            return
        self.var_cat_id.set(row[0])
        self.var_name.set(row[1])

    def delete(self):
        category_id = self.var_cat_id.get().strip()
        if not category_id:
            messagebox.showerror("Error", "Category name must be required", parent=self.root)
            return

        try:
            if not self._run_query("select 1 from category where cid=?", (category_id,), fetchone=True):
                messagebox.showerror("Error", "Invalid Category Name", parent=self.root)
                return

            if not messagebox.askyesno("Confirm", "Do you really want to delete?", parent=self.root):
                return

            self._run_query("delete from category where cid=?", (category_id,))
            messagebox.showinfo("Delete", "Category Deleted Successfully", parent=self.root)
            self.clear()
        except Exception as ex:
            self._handle_error(ex)


if __name__ == "__main__":
    root = Tk()
    obj = categoryClass(root)
    root.mainloop()
