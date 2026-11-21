import logging
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import mysql.connector

from app.database import Student, StudentRepository
from app.validators import (
    parse_date,
    validate_date,
    validate_email,
    validate_enrollment_date,
    validate_name,
    validate_phone,
    validate_study_program,
)


logger = logging.getLogger(__name__)


class StudentManagerApp(tk.Tk):
    # Surfaces
    BG = "#F3F6FA"          # Window background
    SURFACE = "#FFFFFF"     # Forms, table, entry backgrounds
    HEADER = "#E9EFF7"      # Table headings
    ROW_ALT = "#F7F9FC"     # Alternating table rows
    BORDER = "#CFD8E3"      # Borders and separators

    # Text
    TEXT = "#1E293B"        # Main text: dark slate
    MUTED = "#526174"       # Secondary text

    # Primary actions
    ACCENT = "#1D4ED8"      # Add/save buttons
    ACCENT_HOVER = "#1E40AF"
    ACCENT_TEXT = "#FFFFFF"

    # Table selection
    SELECTED = "#DBEAFE"
    SELECTED_TEXT = "#172554"

    # Status and destructive actions
    SUCCESS = "#166534"
    DANGER = "#B42318"
    DANGER_HOVER = "#912018"

    PAGE_SIZE = 10

    def __init__(self):
        super().__init__()
        self.title("Student Manager")
        self.geometry("1120x720")
        self.minsize(900, 600)
        self.configure(bg=self.BG)

        self.repository = None
        self.editing_id = None
        self.current_page = 1
        self.total_students = 0
        self.sort_column = "name"
        self.sort_descending = False
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Connecting to database...")
        self.page_var = tk.StringVar()
        self.connection_var = tk.StringVar(value="Connecting")

        self._configure_style()
        self._build_interface()
        self._connect_to_database()
        self.search_var.trace_add("write", self._search_changed)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def _configure_style(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("Muted.TLabel", background=self.BG, foreground=self.MUTED)
        style.configure(
            "Surface.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT,
        )
        style.configure(
            "SurfaceMuted.TLabel",
            background=self.SURFACE,
            foreground=self.MUTED,
        )
        style.configure(
            "Form.TEntry",
            padding=(9, 7),
            foreground=self.TEXT,
            fieldbackground=self.SURFACE,
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10),
            padding=(14, 5),
            background=self.ACCENT,
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_HOVER)],
            foreground=[("disabled", "#dbeafe")],
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(12, 5),
            background=self.SURFACE,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", self.HEADER)],
        )
        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10),
            padding=(12, 5),
            background=self.SURFACE,
            foreground=self.DANGER,
            bordercolor=self.BORDER,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#fcebea")],
        )
        style.configure(
            "Students.Treeview",
            rowheight=36,
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            borderwidth=0,
        )
        style.configure(
            "Students.Treeview.Heading",
            padding=(10, 10),
            background=self.HEADER,
            foreground=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Students.Treeview", background=[("selected", self.SELECTED)])
        style.configure(
            "Connected.TLabel",
            foreground=self.SUCCESS,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Disconnected.TLabel",
            foreground=self.DANGER,
            font=("Segoe UI", 9, "bold"),
        )

    def _build_interface(self):
        container = ttk.Frame(self, padding=(28, 24))
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(
            header,
            text="Student Manager",
            font=("Segoe UI", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT,
        ).pack(side=tk.LEFT)
        ttk.Label(
            header,
            textvariable=self.connection_var,
            style="Disconnected.TLabel",
        ).pack(side=tk.RIGHT, anchor=tk.N, pady=(8, 0))

        self.list_section = ttk.Frame(container)
        self.list_section.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self.list_section)
        toolbar.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(toolbar, text="Student records", font=("Segoe UI", 15, "bold")).pack(
            side=tk.LEFT
        )
        self._create_button(
            toolbar,
            text="+ New student",
            command=self.open_student_form,
            kind="primary",
        ).pack(side=tk.RIGHT)

        search_frame = ttk.Frame(self.list_section)
        search_frame.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(
            search_frame,
            text="Search name, email, study program, or phone",
            style="Muted.TLabel",
        ).pack(side=tk.LEFT)
        self._create_button(
            search_frame,
            text="Clear",
            command=lambda: self.search_var.set(""),
        ).pack(side=tk.RIGHT)
        ttk.Entry(
            self.list_section,
            textvariable=self.search_var,
            style="Form.TEntry",
        ).pack(fill=tk.X, pady=(0, 14))

        table_frame = ttk.Frame(self.list_section)
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = (
            "id",
            "name",
            "email",
            "date_of_birth",
            "study_program",
            "phone",
            "enrollment_date",
        )
        self.students_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Students.Treeview",
        )
        headings = {
            "id": "ID",
            "name": "Name",
            "email": "Email",
            "date_of_birth": "Date of birth",
            "study_program": "Study program",
            "phone": "Phone",
            "enrollment_date": "Enrollment date",
        }
        widths = {
            "id": 55,
            "name": 160,
            "email": 220,
            "date_of_birth": 110,
            "study_program": 170,
            "phone": 120,
            "enrollment_date": 120,
        }
        for column in columns:
            self.students_table.heading(
                column,
                text=headings[column],
                command=lambda name=column: self.sort_by(name),
            )
            self.students_table.column(
                column,
                width=widths[column],
                minwidth=60,
                anchor=tk.CENTER if column in ("id", "date_of_birth", "enrollment_date") else tk.W,
            )
        self.students_table.bind("<Double-1>", lambda _event: self.show_profile())
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.students_table.yview,
        )
        self.students_table.configure(yscrollcommand=scrollbar.set)
        self.students_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        actions = ttk.Frame(self.list_section)
        actions.pack(fill=tk.X, pady=(14, 0))
        self._create_button(
            actions,
            text="View profile",
            command=self.show_profile,
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(
            actions,
            text="Edit selected",
            command=self.edit_student,
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(
            actions,
            text="Delete selected",
            command=self.delete_student,
            kind="danger",
        ).pack(side=tk.LEFT)
        self._create_button(
            actions,
            text="Refresh",
            command=self.load_students,
        ).pack(side=tk.RIGHT)

        pagination = ttk.Frame(self.list_section)
        pagination.pack(fill=tk.X, pady=(14, 0))
        ttk.Label(pagination, textvariable=self.status_var, style="Muted.TLabel").pack(
            side=tk.LEFT
        )
        self._create_button(
            pagination,
            text="Next",
            command=self.next_page,
        ).pack(side=tk.RIGHT)

        self.form_section = ttk.Frame(container)
        self._build_form_section()
        ttk.Label(pagination, textvariable=self.page_var, style="Muted.TLabel").pack(
            side=tk.RIGHT, padx=12
        )
        self._create_button(
            pagination,
            text="Previous",
            command=self.previous_page,
        ).pack(side=tk.RIGHT)

    def _create_button(self, parent, text, command, kind="secondary", width=None):
        palette = {
            "primary": (self.ACCENT, "white", self.ACCENT_HOVER),
            "secondary": (self.SURFACE, self.TEXT, self.HEADER),
            "danger": (self.SURFACE, self.DANGER, "#fcebea"),
        }
        background, foreground, active_background = palette[kind]
        options = {
            "text": text,
            "command": command,
            "font": ("Segoe UI", 10),
            "bg": background,
            "fg": foreground,
            "activebackground": active_background,
            "activeforeground": foreground,
            "relief": tk.FLAT,
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": self.BORDER,
            "highlightcolor": self.ACCENT,
            "padx": 14,
            "pady": 7,
            "cursor": "hand2",
        }
        if width is not None:
            options["width"] = width
        return tk.Button(parent, **options)

    def _connect_to_database(self):
        try:
            self.repository = StudentRepository()
            self.connection_var.set("● Connected")
            self._set_connection_style("Connected.TLabel")
            self.load_students()
        except (mysql.connector.Error, RuntimeError) as error:
            logger.error("Database connection failed: %s", error)
            self.connection_var.set("● Disconnected")
            self._set_connection_style("Disconnected.TLabel")
            self.status_var.set("Database connection failed.")
            messagebox.showerror(
                "Database connection failed",
                "Could not connect to MySQL. Check your .env settings and server.",
            )

    def _set_connection_style(self, style):
        for child in self.winfo_children():
            self._find_connection_label(child, style)

    def _find_connection_label(self, widget, style):
        if isinstance(widget, ttk.Label) and str(widget.cget("textvariable")):
            if str(widget.cget("textvariable")) == str(self.connection_var):
                widget.configure(style=style)
        for child in widget.winfo_children():
            self._find_connection_label(child, style)

    def load_students(self):
        if self.repository is None:
            return
        try:
            self.total_students = self.repository.count(self.search_var.get())
            total_pages = max(1, (self.total_students + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            self.current_page = min(self.current_page, total_pages)
            students = self.repository.list_students(
                search=self.search_var.get(),
                sort_column=self.sort_column,
                descending=self.sort_descending,
                offset=(self.current_page - 1) * self.PAGE_SIZE,
                limit=self.PAGE_SIZE,
            )
            self._render_students(students)
            self.page_var.set(f"Page {self.current_page} of {total_pages}")
            self.status_var.set(f"{self.total_students} student(s) found.")
        except mysql.connector.Error as error:
            self._show_database_error("Could not load students.", error)

    def _render_students(self, students):
        for item in self.students_table.get_children():
            self.students_table.delete(item)
        for index, student in enumerate(students):
            self.students_table.insert(
                "",
                tk.END,
                iid=str(student.id),
                values=self._display_values(student),
                tags=("even" if index % 2 == 0 else "odd",),
            )
        self.students_table.tag_configure("even", background=self.SURFACE)
        self.students_table.tag_configure("odd", background=self.ROW_ALT)

    @staticmethod
    def _display_values(student):
        return (
            student.id,
            student.name,
            student.email,
            student.date_of_birth.strftime("%d/%m/%Y"),
            student.study_program,
            student.phone,
            student.enrollment_date.strftime("%d/%m/%Y"),
        )

    def _search_changed(self, *_args):
        self.current_page = 1
        self.load_students()

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
        self.load_students()

    def next_page(self):
        if self.current_page * self.PAGE_SIZE < self.total_students:
            self.current_page += 1
            self.load_students()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_students()

    def _selected_id(self):
        selected = self.students_table.selection()
        if not selected:
            messagebox.showinfo("Select a student", "Select a student from the table first.")
            return None
        return int(selected[0])

    def _build_form_section(self):
        frame = tk.Frame(
            self.form_section,
            bg=self.SURFACE,
            padx=28,
            pady=22,
        )
        frame.pack(fill=tk.BOTH, expand=True)
        self.form_title_label = tk.Label(
            frame,
            text="Add a student",
            font=("Segoe UI", 20, "bold"),
            bg=self.SURFACE,
            fg=self.TEXT,
        )
        self.form_title_label.pack(anchor=tk.W)
        ttk.Label(
            frame,
            text="Dates must use DD/MM/YYYY format.",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(5, 16))

        self.form_variables = {
            "name": tk.StringVar(),
            "email": tk.StringVar(),
            "date_of_birth": tk.StringVar(),
            "study_program": tk.StringVar(),
            "phone": tk.StringVar(),
            "enrollment_date": tk.StringVar(),
        }
        self.form_entries = {}
        labels = (
            ("name", "Full name"),
            ("email", "Email address"),
            ("date_of_birth", "Date of birth"),
            ("study_program", "Study program"),
            ("phone", "Phone number"),
            ("enrollment_date", "Enrollment date"),
        )
        for key, label in labels:
            ttk.Label(frame, text=label).pack(anchor=tk.W, pady=(0, 4))
            entry = ttk.Entry(
                frame,
                textvariable=self.form_variables[key],
                style="Form.TEntry",
            )
            entry.pack(fill=tk.X, pady=(0, 9))
            self.form_entries[key] = entry

        buttons = tk.Frame(frame, bg=self.SURFACE)
        buttons.pack(fill=tk.X, pady=(12, 0))
        self.form_save_button = self._create_button(
            buttons,
            text="Save student",
            command=self._save_current_form,
            width=18,
            kind="primary",
        )
        self.form_save_button.pack(side=tk.LEFT, padx=(0, 12))
        self._create_button(
            buttons,
            text="Cancel",
            command=self._show_list_section,
            width=12,
        ).pack(side=tk.LEFT)

    def open_student_form(self, student=None):
        self.editing_id = student.id if student else None
        values = {
            "name": student.name if student else "",
            "email": student.email if student else "",
            "date_of_birth": self._format_date(student.date_of_birth) if student else "",
            "study_program": student.study_program if student else "",
            "phone": student.phone if student else "",
            "enrollment_date": self._format_date(student.enrollment_date) if student else "",
        }
        for key, value in values.items():
            self.form_variables[key].set(value)
        self.form_title_label.configure(
            text="Edit student" if student else "Add a student"
        )
        self.form_save_button.configure(
            text="Save changes" if student else "Save student"
        )
        self.list_section.pack_forget()
        self.form_section.pack(fill=tk.BOTH, expand=True)
        self.form_entries["name"].focus_set()

    def _show_list_section(self):
        self.form_section.pack_forget()
        self.list_section.pack(fill=tk.BOTH, expand=True)
        self._clear_form()

    def _clear_form(self):
        self.editing_id = None
        for variable in self.form_variables.values():
            variable.set("")

    def _save_current_form(self):
        self._save_form(self.form_variables, self.editing_id)

    def _save_form(self, variables, student_id):
        values = {key: variable.get().strip() for key, variable in variables.items()}
        error = self._validate_form(values)
        if error:
            messagebox.showwarning("Invalid student details", error, parent=self)
            return
        try:
            parsed = (
                values["name"],
                values["email"],
                parse_date(values["date_of_birth"]),
                values["study_program"],
                values["phone"],
                parse_date(values["enrollment_date"]),
            )
            if student_id is None:
                self.repository.create(*parsed)
            else:
                self.repository.update(student_id, *parsed)
            self._show_list_section()
            self.load_students()
            self.status_var.set("Student saved successfully.")
        except mysql.connector.IntegrityError as error:
            logger.warning("Student save rejected: %s", error)
            messagebox.showwarning(
                "Duplicate email",
                "The student could not be saved.\n\n"
                f"Database message: {error.msg}",
                parent=self,
            )
        except mysql.connector.Error as error:
            self._show_database_error("Could not save student.", error)

    @staticmethod
    def _validate_form(values):
        if not validate_name(values["name"]):
            return "Name must contain letters and spaces only."
        if not validate_email(values["email"]):
            return "Enter a valid email address."
        if not validate_date(values["date_of_birth"]):
            return "Date of birth must use DD/MM/YYYY format."
        if not validate_study_program(values["study_program"]):
            return "Study program is required and must be at most 100 characters."
        if not validate_phone(values["phone"]):
            return "Enter a valid phone number."
        if not validate_enrollment_date(values["enrollment_date"]):
            return "Enrollment date must be valid and cannot be in the future."
        if parse_date(values["date_of_birth"]) >= date.today():
            return "Date of birth must be in the past."
        return None

    def edit_student(self):
        student_id = self._selected_id()
        if student_id is not None:
            try:
                self.open_student_form(self.repository.get(student_id))
            except mysql.connector.Error as error:
                self._show_database_error("Could not load student.", error)

    def show_profile(self):
        student_id = self._selected_id()
        if student_id is None:
            return
        try:
            student = self.repository.get(student_id)
        except mysql.connector.Error as error:
            self._show_database_error("Could not load student profile.", error)
            return
        if student is None:
            messagebox.showinfo("Student not found", "This student no longer exists.")
            self.load_students()
            return
        profile = tk.Toplevel(self)
        profile.title("Student profile")
        profile.geometry("500x430")
        profile.resizable(False, False)
        profile.transient(self)
        frame = tk.Frame(profile, bg=self.SURFACE, padx=30, pady=26)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(
            frame,
            text=student.name,
            font=("Segoe UI", 20, "bold"),
            bg=self.SURFACE,
            fg=self.TEXT,
        ).pack(anchor=tk.W, pady=(0, 18))
        details = (
            ("Student ID", student.id),
            ("Email", student.email),
            ("Date of birth", self._format_date(student.date_of_birth)),
            ("Study program", student.study_program),
            ("Phone", student.phone),
            ("Enrollment date", self._format_date(student.enrollment_date)),
        )
        for label, value in details:
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=4)
            ttk.Label(row, text=f"{label}:", width=20, style="Muted.TLabel").pack(
                side=tk.LEFT
            )
            ttk.Label(row, text=value).pack(side=tk.LEFT)
        self._create_button(profile, text="Close", command=profile.destroy).pack(
            anchor=tk.W, padx=30, pady=(0, 20)
        )

    def delete_student(self):
        student_id = self._selected_id()
        if student_id is None:
            return
        student = self.repository.get(student_id)
        if student is None:
            self.load_students()
            return
        if not messagebox.askyesno(
            "Confirm deletion",
            f"Delete student '{student.name}'?\n\nThis cannot be undone.",
        ):
            return
        try:
            self.repository.delete(student_id)
            self.load_students()
            self.status_var.set("Student deleted successfully.")
        except mysql.connector.Error as error:
            self._show_database_error("Could not delete student.", error)

    @staticmethod
    def _format_date(value):
        return value.strftime("%d/%m/%Y")

    def _show_database_error(self, message, error):
        logger.error("%s %s", message, error)
        details = f"{message}\n\nMySQL: {error.msg}"
        messagebox.showerror("Database error", details)
        self.status_var.set(f"{message} ({error.errno})")

    def close(self):
        if self.repository is not None:
            self.repository.close()
        self.destroy()


if __name__ == "__main__":
    app = StudentManagerApp()
    app.mainloop()
