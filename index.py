import customtkinter as ctk
import json
import os
import uuid
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog

# ==========================================
# COMMAND CENTER
# Personal Desktop Application
# ==========================================

APP_NAME = "COMMAND CENTER"
DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "CommandCenter"
)
DATA_FILE = os.path.join(DATA_DIR, "data.json")

os.makedirs(DATA_DIR, exist_ok=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Nieprawidłowy format danych.")

            data.setdefault("notes", [])
            data.setdefault("tasks", [])
            data.setdefault("radio", {
                "callsign": "SP7KJR",
                "status": "OFFLINE",
                "frequency": "145.500 MHz"
            })

            return data

        except (json.JSONDecodeError, OSError, ValueError):
            messagebox.showwarning(
                "Dane",
                "Nie udało się odczytać danych. "
                "Uruchomiono pusty zestaw."
            )

    return {
        "notes": [],
        "tasks": [],
        "radio": {
            "callsign": "SP7KJR",
            "status": "OFFLINE",
            "frequency": "145.500 MHz"
        }
    }


data = load_data()


def save_data():
    temp_file = DATA_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    os.replace(temp_file, DATA_FILE)


class CommandCenter(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1100x720")
        self.minsize(850, 580)

        self.current_page = "Dashboard"
        self.search_var = tk.StringVar()
        self.search_var.trace_add(
            "write",
            lambda *_: self.refresh_current_page()
        )

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_content()
        self.show_page("Dashboard")
        self.update_clock()

    # --------------------------------------
    # SIDEBAR
    # --------------------------------------

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=210,
            corner_radius=0
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="COMMAND\nCENTER",
            font=("Arial", 23, "bold"),
            justify="left"
        ).pack(padx=22, pady=(28, 35), anchor="w")

        self.nav_buttons = {}

        pages = [
            ("Dashboard", "⌂  Pulpit"),
            ("Notes", "▤  Notatki"),
            ("Tasks", "✓  Zadania"),
            ("Radio", "◉  Stacja"),
            ("Settings", "⚙  Ustawienia")
        ]

        for page, label in pages:
            button = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=42,
                corner_radius=8,
                command=lambda p=page: self.show_page(p)
            )
            button.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[page] = button

        ctk.CTkLabel(
            self.sidebar,
            text="LOCAL EDITION\nDane pozostają na komputerze",
            font=("Arial", 10),
            text_color="gray"
        ).pack(side="bottom", padx=15, pady=20)

    # --------------------------------------
    # MAIN CONTENT
    # --------------------------------------

    def create_content(self):
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=20
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Pulpit",
            font=("Arial", 28, "bold")
        )
        self.page_title.grid(row=0, column=0, sticky="w")

        self.clock_label = ctk.CTkLabel(
            self.header,
            text="",
            font=("Arial", 13)
        )
        self.clock_label.grid(row=0, column=1, padx=10)

        self.search_entry = ctk.CTkEntry(
            self.content,
            textvariable=self.search_var,
            placeholder_text="Szukaj notatek i zadań..."
        )
        self.search_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(20, 15)
        )

        self.page_area = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        self.page_area.grid(
            row=2,
            column=0,
            sticky="nsew"
        )
        self.page_area.grid_columnconfigure(0, weight=1)
        self.page_area.grid_rowconfigure(0, weight=1)

    def clear_page(self):
        for widget in self.page_area.winfo_children():
            widget.destroy()

    def update_clock(self):
        now = datetime.now()
        self.clock_label.configure(
            text=now.strftime("%d.%m.%Y  |  %H:%M:%S")
        )
        self.after(1000, self.update_clock)

    # --------------------------------------
    # NAVIGATION
    # --------------------------------------

    def show_page(self, page):
        self.current_page = page

        titles = {
            "Dashboard": "Pulpit",
            "Notes": "Notatki",
            "Tasks": "Zadania",
            "Radio": "Panel stacji",
            "Settings": "Ustawienia"
        }

        self.page_title.configure(text=titles[page])

        for name, button in self.nav_buttons.items():
            button.configure(
                fg_color=(
                    ("#1f538d", "#14375e")
                    if name == page else
                    ("#3B8ED0", "#1F6AA5")
                )
            )

        self.refresh_current_page()

    def refresh_current_page(self):
        if not hasattr(self, "page_area"):
            return

        if self.current_page == "Dashboard":
            self.show_dashboard()
        elif self.current_page == "Notes":
            self.show_notes()
        elif self.current_page == "Tasks":
            self.show_tasks()
        elif self.current_page == "Radio":
            self.show_radio()
        elif self.current_page == "Settings":
            self.show_settings()

    # --------------------------------------
    # DASHBOARD
    # --------------------------------------

    def show_dashboard(self):
        self.clear_page()

        wrapper = ctk.CTkScrollableFrame(
            self.page_area,
            fg_color="transparent"
        )
        wrapper.pack(fill="both", expand=True)

        ctk.CTkLabel(
            wrapper,
            text="Witaj w swoim centrum dowodzenia.",
            font=("Arial", 21, "bold")
        ).pack(anchor="w", pady=(5, 20))

        cards = ctk.CTkFrame(
            wrapper,
            fg_color="transparent"
        )
        cards.pack(fill="x")

        cards.grid_columnconfigure((0, 1, 2), weight=1)

        completed = sum(
            1 for task in data["tasks"]
            if task.get("done", False)
        )

        stats = [
            ("NOTATKI", len(data["notes"])),
            ("ZADANIA", len(data["tasks"])),
            ("WYKONANE", completed)
        ]

        for index, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(cards, height=105)
            card.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=5,
                pady=5
            )

            ctk.CTkLabel(
                card,
                text=label,
                text_color="gray",
                font=("Arial", 11, "bold")
            ).pack(pady=(18, 4))

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 27, "bold")
            ).pack()

        ctk.CTkLabel(
            wrapper,
            text="Szybkie akcje",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(25, 10))

        actions = ctk.CTkFrame(
            wrapper,
            fg_color="transparent"
        )
        actions.pack(fill="x")

        ctk.CTkButton(
            actions,
            text="+ Nowa notatka",
            command=lambda: self.show_page("Notes")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            actions,
            text="+ Nowe zadanie",
            command=lambda: self.show_page("Tasks")
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            actions,
            text="Otwórz panel stacji",
            command=lambda: self.show_page("Radio")
        ).pack(fill="x", pady=4)

        ctk.CTkLabel(
            wrapper,
            text="Ostatnie notatki",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(25, 10))

        if not data["notes"]:
            ctk.CTkLabel(
                wrapper,
                text="Nie masz jeszcze notatek."
            ).pack(anchor="w")
        else:
            for note in reversed(data["notes"][-5:]):
                ctk.CTkLabel(
                    wrapper,
                    text="• " + note["title"],
                    anchor="w"
                ).pack(fill="x", pady=3)

    # --------------------------------------
    # NOTES
    # --------------------------------------

    def show_notes(self):
        self.clear_page()

        top = ctk.CTkFrame(
            self.page_area,
            fg_color="transparent"
        )
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top,
            text="+ Nowa notatka",
            command=self.new_note
        ).pack(side="left")

        query = self.search_var.get().strip().lower()

        notes = [
            note for note in data["notes"]
            if query in note.get("title", "").lower()
            or query in note.get("body", "").lower()
        ]

        list_frame = ctk.CTkScrollableFrame(
            self.page_area
        )
        list_frame.pack(fill="both", expand=True)

        if not notes:
            ctk.CTkLabel(
                list_frame,
                text="Brak notatek do wyświetlenia."
            ).pack(pady=20)
            return

        for note in reversed(notes):
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                row,
                text=note["title"],
                font=("Arial", 15, "bold"),
                anchor="w"
            ).pack(
                side="left",
                padx=12,
                pady=12,
                fill="x",
                expand=True
            )

            ctk.CTkButton(
                row,
                text="Otwórz",
                width=85,
                command=lambda n=note: self.edit_note(n)
            ).pack(side="right", padx=5, pady=8)

            ctk.CTkButton(
                row,
                text="Usuń",
                width=65,
                fg_color="#9b3030",
                hover_color="#702020",
                command=lambda n=note: self.delete_note(n)
            ).pack(side="right", padx=5, pady=8)

    def new_note(self):
        self.edit_note({
            "id": str(uuid.uuid4()),
            "title": "",
            "body": "",
            "created": datetime.now().isoformat()
        }, is_new=True)

    def edit_note(self, note, is_new=False):
        window = ctk.CTkToplevel(self)
        window.title("Edytor notatki")
        window.geometry("650x520")
        window.transient(self)
        window.grab_set()

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            window,
            text="Tytuł notatki"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        title_entry = ctk.CTkEntry(window)
        title_entry.grid(row=1, column=0, sticky="ew", padx=20)

        title_entry.insert(0, note.get("title", ""))

        body = ctk.CTkTextbox(window, wrap="word")
        body.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=15
        )
        body.insert("1.0", note.get("body", ""))

        def save_note():
            title = title_entry.get().strip()
            content = body.get("1.0", "end-1c")

            if not title:
                messagebox.showwarning(
                    "Brak tytułu",
                    "Wpisz tytuł notatki.",
                    parent=window
                )
                return

            note["title"] = title
            note["body"] = content
            note["modified"] = datetime.now().isoformat()

            if is_new:
                data["notes"].append(note)

            try:
                save_data()
            except OSError as exc:
                messagebox.showerror(
                    "Błąd zapisu",
                    str(exc),
                    parent=window
                )
                return

            window.destroy()
            self.refresh_current_page()

        ctk.CTkButton(
            window,
            text="Zapisz notatkę",
            command=save_note
        ).grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        title_entry.focus_set()

    def delete_note(self, note):
        if messagebox.askyesno(
            "Usuń notatkę",
            f"Czy usunąć notatkę „{note['title']}”?"
        ):
            data["notes"] = [
                item for item in data["notes"]
                if item["id"] != note["id"]
            ]
            save_data()
            self.refresh_current_page()

    # --------------------------------------
    # TASKS
    # --------------------------------------

    def show_tasks(self):
        self.clear_page()

        top = ctk.CTkFrame(
            self.page_area,
            fg_color="transparent"
        )
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top,
            text="+ Nowe zadanie",
            command=self.new_task
        ).pack(side="left")

        query = self.search_var.get().strip().lower()

        tasks = [
            task for task in data["tasks"]
            if query in task.get("title", "").lower()
        ]

        list_frame = ctk.CTkScrollableFrame(self.page_area)
        list_frame.pack(fill="both", expand=True)

        if not tasks:
            ctk.CTkLabel(
                list_frame,
                text="Brak zadań do wyświetlenia."
            ).pack(pady=20)
            return

        for task in tasks:
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", padx=5, pady=5)

            var = tk.BooleanVar(value=task.get("done", False))

            checkbox = ctk.CTkCheckBox(
                row,
                text=task["title"],
                variable=var,
                command=lambda t=task, v=var: self.toggle_task(t, v)
            )
            checkbox.pack(
                side="left",
                padx=12,
                pady=12,
                fill="x",
                expand=True
            )

            ctk.CTkButton(
                row,
                text="Usuń",
                width=65,
                fg_color="#9b3030",
                hover_color="#702020",
                command=lambda t=task: self.delete_task(t)
            ).pack(side="right", padx=8, pady=8)

    def new_task(self):
        window = ctk.CTkToplevel(self)
        window.title("Nowe zadanie")
        window.geometry("420x180")
        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="Co masz do zrobienia?"
        ).pack(padx=20, pady=(20, 5))

        entry = ctk.CTkEntry(
            window,
            placeholder_text="Nazwa zadania"
        )
        entry.pack(fill="x", padx=20, pady=5)

        def add_task():
            title = entry.get().strip()

            if not title:
                return

            data["tasks"].append({
                "id": str(uuid.uuid4()),
                "title": title,
                "done": False,
                "created": datetime.now().isoformat()
            })

            save_data()
            window.destroy()
            self.refresh_current_page()

        ctk.CTkButton(
            window,
            text="Dodaj zadanie",
            command=add_task
        ).pack(padx=20, pady=10)

        entry.focus_set()

    def toggle_task(self, task, var):
        task["done"] = var.get()
        save_data()
        self.refresh_current_page()

    def delete_task(self, task):
        if messagebox.askyesno(
            "Usuń zadanie",
            f"Czy usunąć „{task['title']}”?"
        ):
            data["tasks"] = [
                item for item in data["tasks"]
                if item["id"] != task["id"]
            ]
            save_data()
            self.refresh_current_page()

    # --------------------------------------
    # RADIO PANEL
    # --------------------------------------

    def show_radio(self):
        self.clear_page()

        radio = data["radio"]

        ctk.CTkLabel(
            self.page_area,
            text="Panel stacji",
            font=("Arial", 23, "bold")
        ).pack(anchor="w", pady=(5, 15))

        form = ctk.CTkFrame(self.page_area)
        form.pack(fill="x", padx=5, pady=5)

        fields = [
            ("Znak wywoławczy", "callsign"),
            ("Status", "status"),
            ("Częstotliwość", "frequency")
        ]

        entries = {}

        for index, (label, key) in enumerate(fields):
            ctk.CTkLabel(
                form,
                text=label
            ).grid(
                row=index,
                column=0,
                sticky="w",
                padx=15,
                pady=12
            )

            entry = ctk.CTkEntry(form, width=260)
            entry.grid(
                row=index,
                column=1,
                sticky="ew",
                padx=15,
                pady=12
            )
            entry.insert(0, str(radio.get(key, "")))
            entries[key] = entry

        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.page_area,
            text=(
                "To lokalne informacje edytowane ręcznie. "
                "Aplikacja nie monitoruje radia."
            ),
            text_color="gray",
            wraplength=600
        ).pack(anchor="w", padx=5, pady=15)

        def save_radio():
            data["radio"] = {
                key: entry.get().strip()
                for key, entry in entries.items()
            }

            try:
                save_data()
            except OSError as exc:
                messagebox.showerror("Błąd zapisu", str(exc))
                return

            messagebox.showinfo(
                "Zapisano",
                "Informacje o stacji zostały zapisane."
            )

        ctk.CTkButton(
            self.page_area,
            text="Zapisz ustawienia stacji",
            command=save_radio
        ).pack(anchor="w", padx=5, pady=10)

    # --------------------------------------
    # SETTINGS
    # --------------------------------------

    def show_settings(self):
        self.clear_page()

        ctk.CTkLabel(
            self.page_area,
            text="Ustawienia",
            font=("Arial", 23, "bold")
        ).pack(anchor="w", pady=(5, 15))

        ctk.CTkLabel(
            self.page_area,
            text="Motyw aplikacji"
        ).pack(anchor="w", pady=5)

        def change_theme(value):
            ctk.set_appearance_mode(value.lower())

        ctk.CTkOptionMenu(
            self.page_area,
            values=["Dark", "Light", "System"],
            command=change_theme
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            self.page_area,
            text="Eksport notatek"
        ).pack(anchor="w", pady=(25, 5))

        ctk.CTkButton(
            self.page_area,
            text="Eksportuj wszystkie notatki",
            command=self.export_notes
        ).pack(anchor="w", pady=5)

        ctk.CTkLabel(
            self.page_area,
            text=f"Lokalizacja danych:\n{DATA_FILE}",
            justify="left",
            wraplength=650
        ).pack(anchor="w", pady=(25, 5))

    def export_notes(self):
        path = filedialog.asksaveasfilename(
            title="Eksportuj notatki",
            defaultextension=".txt",
            filetypes=[("Pliki tekstowe", "*.txt")]
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                for note in data["notes"]:
                    file.write("=" * 50 + "\n")
                    file.write(note["title"] + "\n\n")
                    file.write(note.get("body", "") + "\n\n")

            messagebox.showinfo(
                "Eksport zakończony",
                "Notatki zostały wyeksportowane."
            )

        except OSError as exc:
            messagebox.showerror("Błąd eksportu", str(exc))

    # --------------------------------------
    # EXIT
    # --------------------------------------

    def close_app(self):
        try:
            save_data()
        except OSError as exc:
            if not messagebox.askyesno(
                "Błąd zapisu",
                f"Nie udało się zapisać danych:\n{exc}\n\n"
                "Czy mimo to zamknąć aplikację?"
            ):
                return

        self.destroy()


if __name__ == "__main__":
    app = CommandCenter()
    app.mainloop()
    
