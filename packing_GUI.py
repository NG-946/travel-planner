import tkinter as tk
from tkinter import ttk, messagebox
from constant import CATEGORIES
from storage import StorageManager
from packing_func import (
    add_item, toggle_packed, delete_item,
    get_items, calculate_progress
)

class PackingListFrame:
    def __init__(self, parent, bg_color, frame_bg, button_bg, button_fg, title_bg, back_callback):
        """
        Initialize the PackingListFrame GUI.
        
        parent       : parent window
        bg_color     : main background color
        frame_bg     : left/right panel background color
        button_bg    : button background color
        button_fg    : button text color
        title_bg     : title background color
        back_callback: callback function to return to main menu
        """
        self.parent = parent
        self.back_callback = back_callback
        self.storage = StorageManager()  # data storage manager

        # ---------- Main Frame ----------
        self.frame = tk.Frame(parent, bg=bg_color)

        # ---------- Header ----------
        tk.Label(
            self.frame, text="🧳 Packing List Generator",
            font=("Arial", 20, "bold"),
            bg=title_bg, fg="white", pady=12
        ).pack(fill="x")

        main = tk.Frame(self.frame, padx=20, pady=20, bg=bg_color)
        main.pack(fill="both", expand=True)

        # Left 
        left = tk.Frame(main, bg=frame_bg, bd=2, relief="groove", padx=15, pady=15)
        left.pack(side="left", fill="both", expand=True, padx=10)

        # Right
        right = tk.Frame(main, bg=frame_bg, bd=2, relief="groove", padx=15, pady=15)
        right.pack(side="right", fill="both", expand=True, padx=10)

        # ---------- Left Inputs ----------
        tk.Label(left, text="Select Trip").pack(anchor="w")
        self.trip_cb = ttk.Combobox(left, state="readonly")
        self.trip_cb.pack(fill="x", pady=6)

        tk.Label(left, text="Category").pack(anchor="w")
        self.cat_cb = ttk.Combobox(left, values=CATEGORIES, state="readonly")
        self.cat_cb.current(0)
        self.cat_cb.pack(fill="x", pady=6)

        tk.Label(left, text="Item Name").pack(anchor="w")
        self.item_entry = tk.Entry(left)
        self.item_entry.pack(fill="x", pady=6)

        #Left buttons
        tk.Button(left, text="➕ Add Item", bg=button_bg, fg=button_fg,
                  command=self.add_item).pack(pady=10)

        tk.Button(left, text="💾 Save Data", bg=button_bg, fg=button_fg,
                  command=self.save_data).pack(pady=5)

        tk.Button(left, text="🔙 Back to Main Menu", bg=button_bg, fg=button_fg,
                  command=self.back_callback).pack(pady=5)

        # ---------- Right List ----------
        tk.Label(right, text="Packing List", font=("Arial", 12, "bold")).pack(anchor="w")

        # Listbox to display all items
        self.listbox = tk.Listbox(right, height=18)
        self.listbox.pack(fill="both", expand=True, pady=5)

        btns = tk.Frame(right)
        btns.pack(pady=5)

        # Buttons for Toggle Packed and Delete Item
        tk.Button(btns, text="✔ Toggle Packed", command=self.toggle).pack(side="left", padx=5)
        tk.Button(btns, text="🗑 Delete Item", command=self.delete).pack(side="left", padx=5)

        # Packing progress label and bar
        self.progress_label = tk.Label(right, text="Packing Progress: 0%")
        self.progress_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(right, length=350)
        self.progress_bar.pack(anchor="w")

        # Initial refresh
        self.refresh()

    # ---------- Refresh GUI ----------
    def refresh(self):
        """
        Refresh GUI elements:
        1. Update trip dropdown values
        2. Update Listbox contents
        3. Update packing progress bar
        """
        self.trip_cb["values"] = self.storage.trip_names() # get current trip list

        # Clear and populate Listbox
        self.listbox.delete(0, tk.END)
        for i in get_items():
            status = "✔ Packed" if i["packed"] else "❌ Not Packed"
            self.listbox.insert(
                tk.END,
                f"{i['trip']} | {i['category']} | {i['name']} → {status}"
            )

        # Update progress bar
        progress = calculate_progress()
        self.progress_bar["value"] = progress
        self.progress_label.config(text=f"Packing Progress: {progress}%")

    # ---------- Button ----------
    def add_item(self):
        """Add an item; warn user if input is missing"""
        if self.trip_cb.get() and self.item_entry.get():
            add_item(self.trip_cb.get(), self.cat_cb.get(), self.item_entry.get())
            self.item_entry.delete(0, tk.END)
            self.refresh()
        else:
            messagebox.showwarning("Error", "Missing input") # warn if incomplete

    def toggle(self):
        """
        Toggle packed status of selected item
        Warn user if no item is selected
        """
        if self.listbox.curselection():
            toggle_packed(self.listbox.curselection()[0])
            self.refresh()
        else :
            messagebox.showwarning("Warning","Please select an item to toggle packed.")

    def delete(self):
        """
        Delete selected item
        Warn user if no item is selected
        """
        if self.listbox.curselection():
            delete_item(self.listbox.curselection()[0])
            self.refresh()
        else :
            messagebox.showwarning("Warning","Please select an item to delete.")


    def save_data(self):
        """
        Ask user for confirmation before saving
        Save data and show info message if confirmed
        """
        confirm = messagebox.askyesno("Confirm save","Are you sure you want to save your data?")
        if confirm :
            self.storage.auto_save()
            messagebox.showinfo("Saved", "✅ Your data has been saved!")

    # ---------- Show / Hide ----------
    def show(self):
        """Show the frame"""
        self.refresh()
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        """Hide the frame"""
        self.frame.pack_forget()
