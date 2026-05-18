import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import json
import os
import calendar
from datetime import datetime

DATA_FILE = "notizen.json"

# -----------------------------
# Theme Oblivion-Dark
# -----------------------------
BG_MAIN = "#121212"
BG_PANEL = "#1A1A1A"
FG_TEXT = "#FFFFFF"
BTN_BG = "#2A2A2A"
BTN_ACTIVE_BG = "#3A3A3A"
ENTRY_BG = "#1E1E1E"

HIGHLIGHT_NOTE = "#3F51B5"      # Tage mit Notizen
HIGHLIGHT_TODAY = "#8BC34A"     # Aktueller Tag
HIGHLIGHT_MONTH = "#3949AB"     # Aktueller Monat

FONT_MAIN = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")

# Monate
MONTH_NAMES = [
    "",
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# -----------------------------
# Daten laden / speichern
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()

# -----------------------------
# Export to TXT zusammenfassung
# -----------------------------
def export_txt():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Textdatei", "*.txt")],
        title="Notizen exportieren"
    )
    if not file_path:
        return

    with open(file_path, "w", encoding="utf-8") as f:
        for year in sorted(data.keys()):
            for month in sorted(data[year].keys()):
                for day in sorted(data[year][month].keys()):
                    note = data[year][month][day].strip()
                    if note:
                        f.write(f"{day}.{month}.{year} – {note}\n")

# -----------------------------
# Hauptfenster
# ----------------------------
root = tk.Tk()
root.title("Notizkalender – Oblivion Style")
root.geometry("1350x780")
root.configure(bg=BG_MAIN)

# Icon setzen
try:
    root.iconbitmap("heftchen.ico")
except:
    pass

# Aktuelles Datum
now = datetime.now()
current_year = now.year
current_month = now.month
current_day = now.day

# -----------------------------
# Panels 
# -----------------------------
left_panel = tk.Frame(root, width=260, bg=BG_PANEL)
middle_panel = tk.Frame(root, width=350, bg=BG_PANEL)
right_panel = tk.Frame(root, bg=BG_PANEL)

left_panel.pack(side="left", fill="y")
middle_panel.pack(side="left", fill="y")
right_panel.pack(side="right", fill="both", expand=True)

# -----------------------------
# Jahres-Dropdown
# -----------------------------
year_label = tk.Label(left_panel, text="Jahr auswählen", bg=BG_PANEL, fg=FG_TEXT, font=FONT_TITLE)
year_label.pack(pady=10)

year_var = tk.StringVar(value=str(current_year))
year_dropdown = ttk.Combobox(left_panel, textvariable=year_var, values=[str(y) for y in range(2020, 2036)], state="readonly")
year_dropdown.pack(pady=5)

# -----------------------------
# Monatsliste
# -----------------------------
def load_month(month):
    for widget in middle_panel.winfo_children():
        widget.destroy()

    year = int(year_var.get())
    days_in_month = calendar.monthrange(year, month)[1]

    # 2-Spalten-Layout
    for d in range(1, days_in_month + 1):
        day_str = f"{d:02d}"
        month_str = f"{month:02d}"
        year_str = str(year)

        note_exists = (
            year_str in data and
            month_str in data[year_str] and
            day_str in data[year_str][month_str] and
            data[year_str][month_str][day_str].strip() != ""
        )

        btn = tk.Button(
            middle_panel,
            text=f"{d}. {MONTH_NAMES[month]}",
            width=18,
            anchor="w",
            command=lambda day=d, m=month: load_day(m, day)
        )
        btn.configure(bg=BTN_BG, fg=FG_TEXT, relief="flat", font=FONT_BUTTON)

        # Markierungen
        if year == current_year and month == current_month and d == current_day:
            btn.configure(bg=HIGHLIGHT_TODAY)
        elif note_exists:
            btn.configure(bg=HIGHLIGHT_NOTE)

        row = (d - 1) // 2
        col = (d - 1) % 2
        btn.grid(row=row, column=col, padx=8, pady=4)

def load_day(month, day):
    for widget in right_panel.winfo_children():
        widget.destroy()

    year = int(year_var.get())
    year_str = str(year)
    month_str = f"{month:02d}"
    day_str = f"{day:02d}"

    data.setdefault(year_str, {})
    data[year_str].setdefault(month_str, {})
    data[year_str][month_str].setdefault(day_str, "")

    lbl = tk.Label(right_panel, text=f"Notiz für {day}. {MONTH_NAMES[month]} {year}", bg=BG_PANEL, fg=FG_TEXT, font=FONT_TITLE)
    lbl.pack(pady=10)

    txt = scrolledtext.ScrolledText(right_panel, width=90, height=30, wrap="word")
    txt.pack(padx=10, pady=10)
    txt.configure(bg=ENTRY_BG, fg=FG_TEXT, insertbackground=FG_TEXT, font=FONT_MAIN)

    txt.insert("1.0", data[year_str][month_str][day_str])

    def auto_save(event=None):
        data[year_str][month_str][day_str] = txt.get("1.0", "end").strip()
        save_data(data)

    txt.bind("<KeyRelease>", auto_save)

def show_summary():
    for widget in right_panel.winfo_children():
        widget.destroy()

    lbl = tk.Label(right_panel, text="Zusammenfassung aller Notizen", bg=BG_PANEL, fg=FG_TEXT, font=FONT_TITLE)
    lbl.pack(pady=10)

    txt = scrolledtext.ScrolledText(right_panel, width=90, height=30, wrap="word")
    txt.pack(padx=10, pady=10)
    txt.configure(bg=ENTRY_BG, fg=FG_TEXT, insertbackground=FG_TEXT, font=FONT_MAIN)

    for year in sorted(data.keys()):
        for month in sorted(data[year].keys()):
            for day in sorted(data[year][month].keys()):
                note = data[year][month][day].strip()
                if note:
                    txt.insert("end", f"{day}.{month}.{year} – {note}\n")

# -----------------------------
# Monatsbuttons 
# -----------------------------
for m in range(1, 13):
    btn = tk.Button(
        left_panel,
        text=MONTH_NAMES[m],
        width=20,
        anchor="w",
        command=lambda month=m: load_month(month)
    )
    btn.configure(bg=BTN_BG, fg=FG_TEXT, relief="flat", font=FONT_BUTTON)

    if m == current_month:
        btn.configure(bg=HIGHLIGHT_MONTH)

    btn.pack(pady=5, padx=10)

# -----------------------------
# Buttons: Zusammenfassung + Export
# -----------------------------
summary_btn = tk.Button(left_panel, text="Zusammenfassung anzeigen", command=show_summary)
summary_btn.configure(bg=BTN_BG, fg=FG_TEXT, relief="flat", font=FONT_BUTTON)
summary_btn.pack(pady=10, padx=10)

export_txt_btn = tk.Button(left_panel, text="Notizen als TXT exportieren", command=export_txt)
export_txt_btn.configure(bg=BTN_BG, fg=FG_TEXT, relief="flat", font=FONT_BUTTON)
export_txt_btn.pack(pady=10, padx=10)

# Beim Start aktuellen Monat laden
load_month(current_month)

root.mainloop()
