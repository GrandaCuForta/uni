import logging
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER
from validators import validate_age, validate_email, validate_name


logging.basicConfig(
    filename="student_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class StudentManagerApp(tk.Tk):
    BG = "#f4f7fb"
    SURFACE = "#ffffff"
    TEXT = "#172033"
    MUTED = "#667085"
    ACCENT = "#2563eb"
    ACCENT_HOVER = "#1d4ed8"
    BORDER = "#dce3ed"

    def __init__(self):
        super().__init__()

        self.title("Student Manager")
        self.geometry("980x650")
        self.minsize(760, 520)
        self.configure(bg=self.BG)

        self.connection = None
        self.cursor = None
        self.students = []
        self.editing_id = None

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Connecting to database...")
        self.connection_var = tk.StringVar(value="Connecting")
        self.form_title_var = tk.StringVar(value="Add a student")
        self.form_hint_var = tk.StringVar(
            value="Enter the student's details, then select Save student."
        )

        self._configure_style()
        self._build_interface()
        self._connect_to_database()

        self.search_var.trace_add("write", self._filter_students)
        self.bind("<Control-n>", lambda _event: self.new_student())
        self.bind("<Escape>", lambda _event: self._cancel_form())
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _configure_style(self):
        style = ttk.Style(self)

        # "clam" allows consistent colors across Windows, macOS, and Linux.
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("Muted.TLabel", foreground=self.MUTED)
        style.configure(
            "Form.TEntry",
            padding=(9, 7),
            foreground=self.TEXT,
            fieldbackground=self.SURFACE,
        )
        style.layout("TNotebook.Tab", [])
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(20, 11), font=("Segoe UI", 10))
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.SURFACE)],
            foreground=[("selected", self.ACCENT)],
        )

        style.configure(
            "Accent.TButton",
            padding=(16, 9),
            background=self.ACCENT,
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_HOVER)],
            foreground=[("active", "white")],
        )

        style.configure(
            "Secondary.TButton",
            padding=(14, 9),
            background=self.SURFACE,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#eaf0f9")],
        )

        style.configure(
            "Danger.TButton",
            padding=(14, 9),
            background=self.SURFACE,
            foreground="#b42318",
            bordercolor=self.BORDER,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#feeceb")],
        )

        style.configure(
            "Students.Treeview",
            rowheight=34,
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            borderwidth=0,
        )
        style.configure(
            "Students.Treeview.Heading",
            padding=(10, 10),
            background="#eaf0f9",
            foreground=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Students.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", self.TEXT)],
        )
        style.configure(
            "Connected.TLabel",
            foreground="#087443",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Disconnected.TLabel",
            foreground="#b42318",
            font=("Segoe UI", 9, "bold"),
        )

    def _build_interface(self):
        container = ttk.Frame(self, padding=(28, 24))
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=(0, 22))

        tk.Label(
            header,
            text="Student Manager",
            font=("Segoe UI", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT,
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="Keep student records organized in one place.",
            font=("Segoe UI", 10),
            bg=self.BG,
            fg=self.MUTED,
        ).pack(anchor=tk.W, pady=(4, 0))

        self.connection_badge = ttk.Label(
            header,
            textvariable=self.connection_var,
            style="Disconnected.TLabel",
        )
        self.connection_badge.pack(side=tk.RIGHT, anchor=tk.NE, pady=(8, 0))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.students_tab = ttk.Frame(self.notebook)
        self.details_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.students_tab, text="  Students  ")
        self.notebook.add(self.details_tab, text="  Student details  ")

        self._build_students_tab()
        self._build_details_tab()

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X, pady=(14, 0))

        ttk.Label(
            footer,
            textvariable=self.status_var,
            style="Muted.TLabel",
            anchor=tk.W,
        ).pack(fill=tk.X)

    def _build_students_tab(self):
        page = ttk.Frame(self.students_tab, padding=20)
        page.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(page)
        toolbar.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            toolbar,
            text="Student records",
            font=("Segoe UI", 15, "bold"),
            bg=self.BG,
            fg=self.TEXT,
        ).pack(side=tk.LEFT)

        ttk.Button(
            toolbar,
            text="+ New student",
            style="Accent.TButton",
            command=self.new_student,
        ).pack(side=tk.RIGHT)

        search_row = ttk.Frame(page)
        search_row.pack(fill=tk.X, pady=(0, 14))

        search_header = ttk.Frame(search_row)
        search_header.pack(fill=tk.X)
        ttk.Label(
            search_header,
            text="Search by name or email",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        ttk.Button(
            search_header,
            text="Clear",
            style="Secondary.TButton",
            command=lambda: self.search_var.set(""),
        ).pack(side=tk.RIGHT)

        ttk.Entry(
            search_row,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            style="Form.TEntry",
        ).pack(fill=tk.X, pady=(6, 0))

        table_container = ttk.Frame(page)
        table_container.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "email", "age")
        self.students_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Students.Treeview",
        )

        settings = {
            "id": ("ID", 70, tk.CENTER),
            "name": ("Name", 220, tk.W),
            "email": ("Email", 310, tk.W),
            "age": ("Age", 80, tk.CENTER),
        }

        for column, (heading, width, anchor) in settings.items():
            self.students_table.heading(column, text=heading)
            self.students_table.column(
                column,
                width=width,
                minwidth=60,
                anchor=anchor,
            )

        self.students_table.column("id", stretch=False)
        self.students_table.column("age", stretch=False)
        self.students_table.bind("<Double-1>", self._edit_on_double_click)

        scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            command=self.students_table.yview,
        )
        self.students_table.configure(yscrollcommand=scrollbar.set)

        self.students_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        actions = ttk.Frame(page)
        actions.pack(fill=tk.X, pady=(14, 0))

        ttk.Button(
            actions,
            text="Edit selected",
            style="Secondary.TButton",
            command=self.edit_student,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            actions,
            text="Delete selected",
            style="Danger.TButton",
            command=self.delete_student,
        ).pack(side=tk.LEFT)

        ttk.Button(
            actions,
            text="Refresh",
            style="Secondary.TButton",
            command=self.load_students,
        ).pack(side=tk.RIGHT)

    def _build_details_tab(self):
        outer = ttk.Frame(self.details_tab, padding=24)
        outer.pack(fill=tk.BOTH, expand=True)

        # A centered card keeps the form readable on a wide window.
        card = tk.Frame(
            outer,
            bg=self.SURFACE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            padx=30,
            pady=26,
        )
        card.pack(anchor=tk.N, fill=tk.X, expand=False, padx=70)
        card.columnconfigure(0, weight=1)

        tk.Label(
            card,
            textvariable=self.form_title_var,
            font=("Segoe UI", 18, "bold"),
            bg=self.SURFACE,
            fg=self.TEXT,
        ).grid(row=0, column=0, sticky=tk.W)

        tk.Label(
            card,
            textvariable=self.form_hint_var,
            font=("Segoe UI", 10),
            bg=self.SURFACE,
            fg=self.MUTED,
        ).grid(row=1, column=0, sticky=tk.W, pady=(4, 22))

        self.name_entry = self._add_field(card, "Full name", self.name_var, 2)
        self._add_field(card, "Email address", self.email_var, 4)
        self._add_field(card, "Age", self.age_var, 6)

        buttons = tk.Frame(card, bg=self.SURFACE)
        buttons.grid(row=8, column=0, sticky=tk.W, pady=(14, 0))

        self.save_button = ttk.Button(
            buttons,
            text="Save student",
            style="Accent.TButton",
            command=self.save_student,
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            buttons,
            text="Cancel",
            style="Secondary.TButton",
            command=self._cancel_form,
        ).pack(side=tk.LEFT)

    @staticmethod
    def _add_field(parent, label, variable, row):
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=StudentManagerApp.SURFACE,
            fg=StudentManagerApp.TEXT,
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 6))

        entry = ttk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 11),
            style="Form.TEntry",
        )
        entry.grid(row=row + 1, column=0, sticky=tk.EW, pady=(0, 18))
        return entry

    def _connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            self.cursor = self.connection.cursor()
            self.connection_var.set("● Connected")
            self.connection_badge.configure(style="Connected.TLabel")
            self.load_students()
        except mysql.connector.Error as error:
            logger.error("Database connection failed: %s", error)
            self.status_var.set("Database connection failed.")
            self.connection_var.set("● Disconnected")
            self.connection_badge.configure(style="Disconnected.TLabel")
            messagebox.showerror(
                "Database connection failed",
                "Could not connect to MySQL. Check your .env settings and server.",
            )

    def load_students(self):
        if self.cursor is None:
            self._database_unavailable()
            return

        try:
            self.cursor.execute(
                "SELECT id, name, email, age FROM students ORDER BY id"
            )
            self.students = self.cursor.fetchall()
            self._render_students()
            logger.info("Student list viewed")
        except mysql.connector.Error as error:
            self._show_database_error("Could not load students.", error)

    def _filter_students(self, *_args):
        self._render_students()

    def _render_students(self):
        # Filtering happens in memory; it does not change database records.
        query = self.search_var.get().strip().lower()

        for item in self.students_table.get_children():
            self.students_table.delete(item)

        visible = [
            student
            for student in self.students
            if query in str(student[1]).lower()
            or query in str(student[2]).lower()
        ]

        for index, student in enumerate(visible):
            self.students_table.insert(
                "",
                tk.END,
                iid=str(student[0]),
                values=student,
                tags=("even" if index % 2 == 0 else "odd",),
            )

        self.students_table.tag_configure("even", background=self.SURFACE)
        self.students_table.tag_configure("odd", background="#f8faff")

        if query:
            self.status_var.set(
                f"Showing {len(visible)} of {len(self.students)} students."
            )
        else:
            self.status_var.set(f"{len(self.students)} student(s) loaded.")

    def new_student(self):
        self._clear_form()
        self._set_form_mode()
        self.notebook.select(self.details_tab)
        self.name_entry.focus_set()

    def edit_student(self):
        selected = self._selected_student()
        if selected is None:
            return

        self.editing_id = selected[0]
        self.name_var.set(selected[1])
        self.email_var.set(selected[2])
        self.age_var.set(selected[3])

        self._set_form_mode(self.editing_id)

        self.notebook.select(self.details_tab)
        self.name_entry.focus_set()

    def _edit_on_double_click(self, _event):
        if self.students_table.selection():
            self.edit_student()

    def _set_form_mode(self, student_id=None):
        if student_id is None:
            self.form_title_var.set("Add a student")
            self.form_hint_var.set(
                "Enter the student's details, then select Save student."
            )
            self.save_button.configure(text="Save student")
        else:
            self.form_title_var.set("Edit student")
            self.form_hint_var.set(f"Updating student ID {student_id}.")
            self.save_button.configure(text="Save changes")

    def save_student(self):
        if self.cursor is None:
            self._database_unavailable()
            return

        student = self._read_form()
        if student is None:
            return

        try:
            if self.editing_id is None:
                self.cursor.execute(
                    "INSERT INTO students (name, email, age) VALUES (%s, %s, %s)",
                    student,
                )
                action = "added"
                logger_message = "Student added"
            else:
                student_id = self.editing_id
                self.cursor.execute(
                    "UPDATE students "
                    "SET name = %s, email = %s, age = %s "
                    "WHERE id = %s",
                    (*student, student_id),
                )
                action = "updated"
                logger_message = f"Student updated: ID {student_id}"

            self.connection.commit()
            logger.info("%s", logger_message)

            self._clear_form()
            self.load_students()
            self.notebook.select(self.students_tab)
            self.status_var.set(f"Student {action} successfully.")

        except mysql.connector.IntegrityError:
            self._show_duplicate_email()
        except mysql.connector.Error as error:
            self._show_database_error("Could not save student.", error)

    def delete_student(self):
        if self.cursor is None:
            self._database_unavailable()
            return

        selected = self._selected_student()
        if selected is None:
            return

        student_id, name = selected[0], selected[1]

        if not messagebox.askyesno(
            "Confirm deletion",
            f"Delete student '{name}'?\n\nThis cannot be undone.",
        ):
            return

        try:
            self.cursor.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,),
            )
            self.connection.commit()

            logger.info("Student deleted: ID %s", student_id)
            self.load_students()
            self.status_var.set("Student deleted successfully.")

        except mysql.connector.Error as error:
            self._show_database_error("Could not delete student.", error)

    def _selected_student(self):
        selected = self.students_table.selection()
        if not selected:
            messagebox.showinfo(
                "Select a student",
                "Select a student from the table first.",
            )
            return None

        student = self.students_table.item(selected[0], "values")
        self.status_var.set(f"Selected student: {student[1]}")
        return student

    def _read_form(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        age = self.age_var.get().strip()

        if not validate_name(name):
            messagebox.showwarning("Invalid name", "Name cannot be empty.")
            return None

        if not validate_email(email):
            messagebox.showwarning("Invalid email", "Email must contain @.")
            return None

        if not validate_age(age):
            messagebox.showwarning(
                "Invalid age",
                "Age must be a number from 0 to 120.",
            )
            return None

        return name, email, int(age)

    def _clear_form(self):
        self.editing_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.age_var.set("")

    def _cancel_form(self):
        self._clear_form()
        self._set_form_mode()
        self.notebook.select(self.students_tab)

    def _database_unavailable(self):
        messagebox.showerror(
            "Database unavailable",
            "The database is not connected. Check MySQL and restart the app.",
        )

    def _rollback(self):
        if self.connection is not None:
            try:
                self.connection.rollback()
            except mysql.connector.Error:
                logger.exception("Could not roll back database transaction")

    def _show_duplicate_email(self):
        self._rollback()
        messagebox.showwarning(
            "Duplicate email",
            "This email address is already registered.",
        )

    def _show_database_error(self, message, error):
        self._rollback()
        logger.error("%s %s", message, error)
        messagebox.showerror("Database error", message)
        self.status_var.set(message)

    def close(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None and self.connection.is_connected():
                self.connection.close()
        except mysql.connector.Error:
            logger.exception("Error while closing database connection")
        finally:
            self.destroy()


if __name__ == "__main__":
    app = StudentManagerApp()
    app.mainloop()