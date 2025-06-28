import os
import json
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox
from time import sleep, ctime, time
import threading
from bs4 import BeautifulSoup
import pyperclip

# ---------------- Configuration ----------------
CONFIG_FILE = "config.json"
VERSIONS_DIR = "form_versions"
DEFAULT_FORM_LINKS = {
    'I-765': 'https://www.uscis.gov/sites/default/files/document/forms/i-765.pdf',
    'I-485': 'https://www.uscis.gov/sites/default/files/document/forms/i-485.pdf',
    'I-485A': 'https://www.uscis.gov/sites/default/files/document/forms/i-485supa.pdf',
    'I-130': 'https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf',
    'I-130A': 'https://www.uscis.gov/sites/default/files/document/forms/i-130a.pdf',
    'I-821D': 'https://www.uscis.gov/sites/default/files/document/forms/i-821d.pdf',
    'I-821': 'https://www.uscis.gov/sites/default/files/document/forms/i-821.pdf',
    'I-134': 'https://www.uscis.gov/sites/default/files/document/forms/i-134.pdf',
    'I-140': 'https://www.uscis.gov/sites/default/files/document/forms/i-140.pdf',
    'I-129F': 'https://www.uscis.gov/sites/default/files/document/forms/i-129f.pdf',
    'I-131': 'https://www.uscis.gov/sites/default/files/document/forms/i-131.pdf',
    'I-539': 'https://www.uscis.gov/sites/default/files/document/forms/i-539.pdf',
    'I-589': 'https://www.uscis.gov/sites/default/files/document/forms/i-589.pdf',
    'I-612': 'https://www.uscis.gov/sites/default/files/document/forms/i-612.pdf',
    'I-751': 'https://www.uscis.gov/sites/default/files/document/forms/i-751.pdf',
    'I-817': 'https://www.uscis.gov/sites/default/files/document/forms/i-817.pdf',
    'I-824': 'https://www.uscis.gov/sites/default/files/document/forms/i-824.pdf',
    'I-864': 'https://www.uscis.gov/sites/default/files/document/forms/i-864.pdf',
    'I-864A': 'https://www.uscis.gov/sites/default/files/document/forms/i-864a.pdf',
    'I-864EZ': 'https://www.uscis.gov/sites/default/files/document/forms/i-864ez.pdf',
    'I-864P': 'https://www.uscis.gov/sites/default/files/document/forms/i-864.pdf',
    'I-881': 'https://www.uscis.gov/sites/default/files/document/forms/i-881.pdf',
    'I-912': 'https://www.uscis.gov/sites/default/files/document/forms/i-912.pdf',
    'N-400': 'https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf',
    'N-565': 'https://www.uscis.gov/sites/default/files/document/forms/n-565.pdf',
    'N-600': 'https://www.uscis.gov/sites/default/files/document/forms/n-600.pdf',
    'I-90': 'https://www.uscis.gov/sites/default/files/document/forms/i-90.pdf',
    'AR-11': 'https://www.uscis.gov/sites/default/files/document/forms/ar-11.pdf',
    'EOIR-29': 'https://www.uscis.gov/sites/default/files/document/forms/eoir-29.pdf',
    'G-325A': 'https://www.uscis.gov/sites/default/files/document/forms/g-325a.pdf',
    'G-639': 'https://www.uscis.gov/sites/default/files/document/forms/g-639.pdf',
    'G-1055': 'https://www.uscis.gov/sites/default/files/document/forms/g-1055.pdf',
    'G-1450': 'https://www.uscis.gov/sites/default/files/document/forms/g-1450.pdf'

}

LIVE_USCIS_FORMS_URL = "https://www.uscis.gov/forms/all-forms"

# ---------------- Persistence ----------------
def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving config:", e)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_versioned_forms(form_data):
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    timestamp = time()
    timestr = ctime(timestamp).replace(":", "-").replace(" ", "_")
    filename = os.path.join(VERSIONS_DIR, f"forms_{timestr}.json")
    with open(filename, "w") as f:
        json.dump(form_data, f, indent=2)

config = load_config()
forms = dict(sorted(config.get("forms", DEFAULT_FORM_LINKS.copy()).items()))
last_folder = config.get("last_folder", "")
appearance_mode = config.get("theme", "dark")
last_checked_timestamp = config.get("last_checked", "Never")
form_versions = config.get("form_versions", {})

# ---------------- Theme and UI Setup ----------------
ctk.set_appearance_mode(appearance_mode)
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("USCIS by Chino. (v1.0)")
app.geometry("900x800")

search_var = ctk.StringVar()
folder_var = ctk.StringVar(value=last_folder)
theme_var = ctk.StringVar(value=appearance_mode)

# ---------------- Folder Picker ----------------
folder_frame = ctk.CTkFrame(app, corner_radius=10)
folder_frame.pack(padx=20, pady=(10, 5), fill='x')
ctk.CTkLabel(folder_frame, text="Download Folder:").pack(side="left", padx=(10, 5))
ctk.CTkEntry(folder_frame, textvariable=folder_var, width=400).pack(side="left", padx=5)
ctk.CTkButton(folder_frame, text="Browse", command=lambda: folder_var.set(filedialog.askdirectory())).pack(side="left", padx=5)

# ---------------- Toolbar ----------------
toolbar_frame = ctk.CTkFrame(app)
toolbar_frame.pack(padx=20, pady=(5, 10), fill='x')

# Theme toggle switch on far right, no label text
theme_switch = ctk.CTkSwitch(toolbar_frame, text="", variable=theme_var, onvalue="light", offvalue="dark",
                             command=lambda: [ctk.set_appearance_mode(theme_var.get()), config.update({"theme": theme_var.get()}), save_config(config)])
theme_switch.pack(side="right", padx=10)

last_checked_label = ctk.CTkLabel(toolbar_frame, text=f"Last Checked: {last_checked_timestamp}")
last_checked_label.pack(side="left", padx=10)
version_history_label = ctk.CTkLabel(toolbar_frame, text=f"Forms Loaded: {len(forms)}")
version_history_label.pack(side="left", padx=10)

# Check for Updates
def check_for_updates():
    def update_task():
        try:
            response = requests.get(LIVE_USCIS_FORMS_URL, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                updated = False
                versions = {}
                new_forms = {}
                for a in links:
                    href = a['href']
                    text = a.get_text(strip=True)
                    if href.endswith(".pdf") and len(text) <= 10 and text.startswith("I-"):
                        form_name = text
                        full_url = "https://www.uscis.gov" + href if href.startswith("/sites") else href
                        new_forms[form_name] = full_url
                        versions[form_name] = full_url
                        if form_name not in forms or forms[form_name] != full_url:
                            updated = True
                if updated:
                    save_versioned_forms(new_forms)
                    forms.clear()
                    forms.update(new_forms)
                    config["forms"] = forms
                config["form_versions"] = versions
                global last_checked_timestamp
                last_checked_timestamp = ctime(time())
                config["last_checked"] = last_checked_timestamp
                save_config(config)
                rebuild_form_list()
                last_checked_label.configure(text=f"Last Checked: {last_checked_timestamp}")
                version_history_label.configure(text=f"Forms Loaded: {len(forms)}")
                messagebox.showinfo("Update Check", "Forms updated successfully." if updated else "No updates found.")
            else:
                messagebox.showwarning("Update Failed", "Could not fetch update data.")
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

    threading.Thread(target=update_task, daemon=True).start()

ctk.CTkButton(toolbar_frame, text="Check for Updates", command=check_for_updates).pack(side="left", padx=10)

# Version History Viewer
def show_version_history():
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    history_win = ctk.CTkToplevel()
    history_win.title("Version History")
    history_win.geometry("600x500")

    listbox = ctk.CTkTextbox(history_win, width=580, height=400)
    listbox.pack(pady=10, padx=10)

    def load_diff(file):
        try:
            with open(file, 'r') as f:
                version_data = json.load(f)
            diff = [f"{k}: {version_data[k]}" for k in sorted(version_data)]
            listbox.configure(state="normal")
            listbox.delete("1.0", "end")
            listbox.insert("end", "\n".join(diff))
            listbox.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    for fname in sorted(os.listdir(VERSIONS_DIR), reverse=True):
        if fname.endswith(".json"):
            full_path = os.path.join(VERSIONS_DIR, fname)
            btn = ctk.CTkButton(history_win, text=fname, command=lambda f=full_path: load_diff(f))
            btn.pack(pady=2)

ctk.CTkButton(toolbar_frame, text="Version History", command=show_version_history).pack(side="left", padx=10)

# ---------------- State Variables ----------------
selected_forms = {}
form_rows = {}
edit_state = {"active": False, "form_key": None}
name_var = ctk.StringVar()
url_var = ctk.StringVar()

# ---------------- Search Bar ----------------
search_entry = ctk.CTkEntry(app, textvariable=search_var, placeholder_text="Search")
search_entry.pack(padx=20, pady=(10, 5), fill="x")

# ---------------- Form Selection Area ----------------
scroll_frame = ctk.CTkScrollableFrame(app, label_text="Select Forms to Download")
scroll_frame.pack(padx=20, pady=(5, 5), fill='both', expand=True)
last_width = [0]  # Used to track previous width for resize detection

def on_scroll_frame_resize(event):
    new_width = scroll_frame.winfo_width()
    if abs(new_width - last_width[0]) > 30:
        last_width[0] = new_width
        if hasattr(app, "_resize_after_id"):
            app.after_cancel(app._resize_after_id)
        app._resize_after_id = app.after(300, preserve_scroll_and_rebuild)



scroll_frame.bind("<Configure>", on_scroll_frame_resize)

def rebuild_form_list():
    scroll_frame.update_idletasks()

    # Clear previous children
    for widget in scroll_frame.winfo_children():
        widget.destroy()
    selected_forms.clear()
    form_rows.clear()

    # Create a centered container frame inside scroll_frame
    container = ctk.CTkFrame(scroll_frame)
    container.pack(pady=10)

    query = search_var.get().lower().strip()
    items = [k for k in sorted(forms) if query in k.lower()] if query else sorted(forms)

    frame_width = scroll_frame.winfo_width()
    approx_column_width = 280
    cols = max(1, frame_width // approx_column_width)

    total_used_width = cols * approx_column_width
    extra_space = max(0, frame_width - total_used_width)
    start_col = max(0, extra_space // 2 // approx_column_width)

    for i, form in enumerate(items):
        row, col = divmod(i, cols)
        frame = ctk.CTkFrame(container)
        frame.grid(row=row, column=col + start_col, padx=5, pady=5, sticky="w")

        var = ctk.BooleanVar(value=True)
        chk = ctk.CTkCheckBox(frame, text=form, variable=var)
        chk.pack(side="left")

        edit_btn = ctk.CTkButton(frame, text="Edit", width=40, command=lambda f=form: edit_form_prompt(f))
        edit_btn.configure(fg_color="#2A7DE1", hover_color="#1E5BB8", text_color="white")
        edit_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(frame, text="Delete", width=60, fg_color="#C03C3C", hover_color="#9A2B2B", text_color="white",
                                command=lambda f=form: delete_form(f))
        del_btn.pack(side="left", padx=2)

        selected_forms[form] = var
        form_rows[form] = frame

    scroll_frame._parent_canvas.configure(scrollregion=scroll_frame._parent_canvas.bbox("all"))



search_var.trace_add("write", lambda *_: rebuild_form_list())
rebuild_form_list()

# ---------------- Add/Edit Panel ----------------
link_frame = ctk.CTkFrame(app)
link_frame.pack(padx=20, pady=(5, 5), fill='x')

left = ctk.CTkFrame(link_frame)
right = ctk.CTkFrame(link_frame, width=100)
left.pack(side="left", expand=True, fill="x", padx=5)
right.pack(side="left", fill="y", padx=5)

# Left side - vertical stack
ctk.CTkLabel(left, text="Form Name:").pack(anchor="w", pady=(0,2))
ctk.CTkEntry(left, textvariable=name_var).pack(fill="x", pady=(0,10))

ctk.CTkLabel(left, text="Form URL:").pack(anchor="w", pady=(0,2))
url_entry = ctk.CTkEntry(left, textvariable=url_var)
url_entry.pack(fill="x")

# Paste button inside URL entry frame
def paste_url():
    try:
        url_var.set(pyperclip.paste())
    except Exception:
        pass

paste_btn = ctk.CTkButton(left, text="Paste", width=60, command=paste_url)
paste_btn.pack(pady=(5,0), anchor="e")

# Right side - Save button centered vertically
def center_save_btn(event=None):
    right.update_idletasks()
    height = right.winfo_height()
    btn_height = save_btn.winfo_height()
    y_pad = max((height - btn_height)//2, 0)
    save_btn.pack_configure(pady=(y_pad, y_pad))

save_btn = ctk.CTkButton(right, text="Save", command=lambda: add_or_edit_link())
save_btn.pack(pady=10)
right.bind("<Configure>", center_save_btn)

def add_or_edit_link():
    name = name_var.get().strip()
    url = url_var.get().strip()
    if not name or not url:
        return messagebox.showerror("Error", "Both fields required.")
    if edit_state["active"]:
        old = edit_state["form_key"]
        if old in forms and old != name:
            del forms[old]
        forms[name] = url
        edit_state["active"] = False
        edit_state["form_key"] = None
    else:
        if name in forms:
            return messagebox.showerror("Duplicate", "Form already exists.")
        forms[name] = url
    config["forms"] = forms
    save_config(config)
    name_var.set("")
    url_var.set("")
    rebuild_form_list()

def edit_form_prompt(key):
    name_var.set(key)
    url_var.set(forms[key])
    edit_state["active"] = True
    edit_state["form_key"] = key

def delete_form(key):
    if messagebox.askyesno("Delete", f"Delete {key}?"):
        del forms[key]
        config["forms"] = forms
        save_config(config)
        rebuild_form_list()

# ---------------- Button Bar ----------------
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(padx=20, pady=10)

def download_selected():
    def task():
        folder = folder_var.get()
        if not folder:
            return messagebox.showerror("Folder", "Select a folder.")
        selected = [f for f, v in selected_forms.items() if v.get()]
        if not selected:
            return messagebox.showerror("Forms", "Select at least one form.")

        log_box.configure(state="normal")
        log_box.delete("1.0", "end")
        log_box.configure(state="disabled")

        errors = []
        for form in selected:
            url = forms[form]
            path = os.path.join(folder, f"{form}.pdf")
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200 and 'pdf' in r.headers.get("Content-Type", ""):
                    with open(path, "wb") as f:
                        f.write(r.content)
                    log(f"✅ {form} downloaded.")
                else:
                    raise Exception(f"Invalid content")
            except Exception as e:
                error_msg = f"❌ {form} failed: {str(e)}"
                log(error_msg)
                errors.append(error_msg)
            sleep(0.2)

        if errors:
            messagebox.showwarning("Download Completed", f"Download finished with {len(errors)} error(s). Check log for details.")
        else:
            messagebox.showinfo("Download Completed", "All selected forms downloaded successfully.")

    threading.Thread(target=task, daemon=True).start()

def log(msg):
    log_box.configure(state="normal")
    log_box.insert("end", msg + "\n")
    log_box.see("end")
    log_box.configure(state="disabled")

def view_files():
    folder = folder_var.get()
    if folder and os.path.exists(folder):
        os.startfile(folder)

ctk.CTkButton(btn_frame, text="Start Download", command=download_selected, width=160, fg_color="#4CAF50").pack(side="left", padx=5)
ctk.CTkButton(btn_frame, text="View Downloads", command=view_files, width=160, fg_color="#2196F3").pack(side="left", padx=5)
ctk.CTkButton(btn_frame, text="Exit", command=app.destroy, width=100, fg_color="red").pack(side="left", padx=5)

# ---------------- Log Console ----------------
log_box = ctk.CTkTextbox(app, height=150)
log_box.pack(padx=20, pady=(5, 20), fill="both")
log_box.configure(state="disabled")

# ✅ Bind window resize to dynamic layout update
resize_timer = [None]

def on_resize(event):
    if resize_timer[0]:
        app.after_cancel(resize_timer[0])
    resize_timer[0] = app.after(400, preserve_scroll_and_rebuild)

def preserve_scroll_and_rebuild():
    rebuild_form_list()
    try:
        scroll_frame._parent_canvas.yview_moveto(0)
    except Exception as e:
        print("Scroll restore failed:", e)
        try:
            scroll_frame._parent_canvas.yview_moveto(pos[0])  # Restore scroll
        except Exception as e:
            print("Scroll restore failed:", e)

    app.after(50, delayed_rebuild)  # slight delay to let layout settle
    def on_scroll_frame_resize(event):
        new_width = scroll_frame.winfo_width()
        if abs(new_width - last_width[0]) > 30:
            last_width[0] = new_width
            preserve_scroll_and_rebuild()

scroll_frame.bind("<Configure>", on_scroll_frame_resize)

# ---------------- Launch App ----------------
app.mainloop()