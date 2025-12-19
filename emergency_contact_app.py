"""Emergency Contact module integrated into main app"""
import tkinter as tk
from tkinter import ttk, messagebox
import json

class Person:
    def __init__(self, name, phone_num, email, address):
        self.name = name
        self.phone = phone_num
        self.email = email
        self.address = address

class EmergencyContact(Person):
    def __init__(self, name, phone, email, address, relationship = "Family", primary = False):
        super().__init__(name, phone, email, address)
        self.relationship = relationship
        self.primary = primary
        self.id = None

class ContactManager:
    def __init__(self):
        self.contacts = []
        self.contact_id_counter = 1
        self.editing_contact_id = None
        
    def add_contact(self, contact: EmergencyContact):
        contact.id = self.contact_id_counter
        self.contacts.append(contact)
        self.contact_id_counter += 1

    def delete_contact(self, contact_id):
        self.contacts = [c for c in self.contacts if c.id != contact_id]

    def get_contact(self, contact_id):
        return next((c for c in self.contacts if c.id == contact_id), None)
    
    def is_duplicate(self, name, phone, email, ignore_id = None):
        for c in self.contacts:
            if ignore_id and c.id == ignore_id:
                continue
            if (c.name == name or c.phone == phone or c.email == email):
                return True
        return False
    
    def save_to_file(self, filename="emergency_contacts.json"):
        with open(filename, "w") as f:
            json.dump([{
                "id" : c.id,
                "name" : c.name,
                "phone number" : c.phone,
                "email" : c.email,
                "relationship" : c.relationship,
                "address" : c.address,
                "primary" : c.primary
            }for c in self.contacts], f, indent=4)
    
    def load_from_file(self, filename="emergency_contacts.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.contacts = []
            for c in data:
                contact = EmergencyContact(
                    name = c["name"],
                    phone = c["phone number"],
                    email = c["email"],
                    address = c["address"],
                    relationship= c["relationship"],
                    primary = c["primary"]
                )
                contact.id = c["id"]
                self.contacts.append(contact)
            if self.contacts:
                self.contact_id_counter = max(c.id for c in self.contacts) + 1 
        except FileNotFoundError:
            self.contacts = []

class EmergencyContactModule:
    def __init__(self, parent_frame, bg_color, frame_bg, button_bg, button_fg, title_bg, back_callback=None):
        """
        Initialize the Emergency Contact Module
        
        Args:
            parent_frame: The parent tkinter frame
            bg_color: Background color
            frame_bg: Frame background color
            button_bg: Button background color
            button_fg: Button foreground color
            title_bg: Title background color
            back_callback: Optional callback function for back button
        """
        self.parent = parent_frame
        self.bg_color = bg_color
        self.frame_bg = frame_bg
        self.button_bg = button_bg
        self.button_fg = button_fg
        self.title_bg = title_bg
        self.back_callback = back_callback
        
        # Initialize contact manager
        self.contact_manage = ContactManager()
        self.contact_manage.load_from_file()
        
        # Widgets
        self.tree = None
        self.name_entry = None
        self.phone_num_entry = None
        self.email_entry = None
        self.relationship_combo = None
        self.address_entry = None
        self.primary_var = None
        
        self.setup_gui()
        self.update_emergency_view()
    
    def setup_gui(self):
        """Setup the complete GUI"""
        # Clear parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Add title
        tk.Label(self.parent, text="📞 Emergency Contact", font=("Arial", 20, "bold"), 
                bg=self.title_bg, fg="white", padx=20, pady=10).pack(fill="x")
        
        # Main content frame
        content_frame = tk.Frame(self.parent, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Split into left (list) and right (form) frames
        left_frame = tk.Frame(content_frame, bg=self.bg_color)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(content_frame, bg=self.bg_color)
        right_frame.pack(side="right", fill="y")
        
        # Setup tree view (left)
        self.setup_tree_view(left_frame)
        
        # Setup form (right)
        self.setup_contact_form(right_frame)
    
    def setup_tree_view(self, parent):
        """Setup the treeview for displaying contacts"""
        # Tree container
        tree_container = tk.Frame(parent)
        tree_container.pack(fill="both", expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_container, columns=("Name", "Phone", "Email", "Address", "Primary"), 
                                show="tree headings")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure tree columns
        self.tree.heading("#0", text="Category", anchor="w")
        self.tree.heading("Name", text="Contact Name")
        self.tree.heading("Phone", text="Phone Number")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Primary", text="Primary")
        
        self.tree.column("#0", width=120, stretch=tk.NO)
        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=100)
        self.tree.column("Email", width=150)
        self.tree.column("Address", width=100)
        self.tree.column("Primary", width=70, anchor="center", stretch=tk.NO)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Tree buttons frame
        tree_btn_frame = tk.Frame(parent, bg=self.bg_color)
        tree_btn_frame.pack(fill="x", pady=5)
        
        # Edit button
        edit_btn = tk.Button(tree_btn_frame, text="✏️ Edit Selected", width=15,
                            bg=self.button_bg, fg=self.button_fg,
                            command=self.edit_selected_contact, cursor="hand2")
        edit_btn.pack(side="left", padx=5)
        
        # Delete button
        delete_btn = tk.Button(tree_btn_frame, text="❌ Delete Selected", width=15,
                              bg=self.button_bg, fg=self.button_fg,
                              command=self.delete_selected_contact, cursor="hand2")
        delete_btn.pack(side="left", padx=5)
    
    def setup_contact_form(self, parent):
        """Setup the contact form for adding/editing contacts"""
        # Contact Name
        tk.Label(parent, text="Contact Name", bg=self.frame_bg, font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", padx=20, pady=(10, 0))
        self.name_entry = tk.Entry(parent, width=35, font=("Arial", 11))
        self.name_entry.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Phone Number
        tk.Label(parent, text="Phone Number", bg=self.frame_bg, font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", padx=20)
        self.phone_num_entry = tk.Entry(parent, width=35, font=("Arial", 11))
        self.phone_num_entry.grid(row=3, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Email
        tk.Label(parent, text="Email", bg=self.frame_bg, font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", padx=20)
        self.email_entry = tk.Entry(parent, width=35, font=("Arial", 11))
        self.email_entry.grid(row=5, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Relationship
        tk.Label(parent, text="Relationship", bg=self.frame_bg, font=("Arial", 10)).grid(
            row=6, column=0, sticky="w", padx=20)
        self.relationship_combo = ttk.Combobox(parent, values=["Family", "Friend", "Emergency", "Travel Related"],
                                              font=("Arial", 11), width=32, state="readonly")
        self.relationship_combo.grid(row=7, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.relationship_combo.set("Family")
        
        # Address
        tk.Label(parent, text="Address", bg=self.frame_bg, font=("Arial", 10)).grid(
            row=8, column=0, sticky="w", padx=20)
        self.address_entry = tk.Text(parent, width=35, height=3, font=("Arial", 11))
        self.address_entry.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Primary Contact Checkbox
        self.primary_var = tk.BooleanVar()
        self.primary_check = tk.Checkbutton(
            parent, text="Primary Contact", font=("Arial", 11), bg=self.frame_bg,
            variable=self.primary_var, command=self.on_primary_toggle, cursor="hand2"
        )
        self.primary_check.grid(row=10, column=0, sticky="w", padx=20, pady=(5, 10))
        
        # Buttons frame
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.grid(row=11, column=0, pady=(10, 0))
        
        # Save button
        save_btn = tk.Button(button_frame, text="💾 Save Contact", width=15, height=1,
                            font=("Arial", 10), bg=self.button_bg, fg=self.button_fg,
                            command=self.save_emergency_contact, cursor="hand2")
        save_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = tk.Button(button_frame, text="🗑️ Clear Form", width=15, height=1,
                             font=("Arial", 10), bg=self.button_bg, fg=self.button_fg,
                             command=self.clear_emergency_form, cursor="hand2")
        clear_btn.pack(side="left", padx=5)
        
        # Add a separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.grid(row=12, column=0, sticky="ew", padx=20, pady=20)
        
        # Back button (if callback provided)
        if self.back_callback:
            back_btn = tk.Button(parent, text="🔙 Back to Main Menu", width=20, height=1,
                                font=("Arial", 10), bg=self.button_bg, fg=self.button_fg,
                                command=self.back_callback, cursor="hand2")
            back_btn.grid(row=13, column=0, pady=(10, 0))
    
    def on_primary_toggle(self):
        """Handle primary contact toggle"""
        if self.primary_var.get():
            category = self.relationship_combo.get()
            editing_id = self.contact_manage.editing_contact_id

            primary_contacts = [c for c in self.contact_manage.contacts
                                if c.relationship == category and c.primary and c.id != editing_id]
            
            if len(primary_contacts) >=2:
                replace = messagebox.askyesno(
                    "Maximum Primary Reached",
                    f"There are already 2 primary contacts in '{category}'.\n"
                    "Do you want to replace one of them with this contact?"
                )
                if replace:
                    primary_contacts.sort(key= lambda c: c.id)
                    primary_contacts[0].primary = False
                else:
                    self.primary_var.set(False)
    
    def save_emergency_contact(self):
        """Save or update an emergency contact"""
        name = self.name_entry.get().strip()
        phone_num = self.phone_num_entry.get().strip()
        email = self.email_entry.get().strip()
        relationship = self.relationship_combo.get().strip()
        address = self.address_entry.get("1.0", tk.END).strip()
        primary = self.primary_var.get()
        
        # Validation
        if not name or not phone_num or not email or not address:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if not phone_num.isdigit():
            messagebox.showerror("Invalid Input", "Phone number must contain digits only.")
            self.phone_num_entry.focus()
            return
        
        if self.contact_manage.is_duplicate(
            name, phone_num, email, address, 
            ignore_id= self.contact_manage.editing_contact_id
        ):
            messagebox.showerror(
                "Duplicate Contact",
                "This contact already exists.\nPlease enter different details."
            )
            return
        
        # Update existing contact or add new one
        if self.contact_manage.editing_contact_id:
            contact = self.contact_manage.get_contact(self.contact_manage.editing_contact_id)
            if contact:
                contact.name = name
                contact.phone = phone_num
                contact.email = email
                contact.relationship = relationship
                contact.address = address
                contact.primary = primary
            self.contact_manage.editing_contact_id = None
            action = "updated"
        else:
            new_contact = EmergencyContact(
                name=name,
                phone=phone_num,
                email=email,
                address=address,
                relationship=relationship,
                primary=primary
                )
            self.contact_manage.add_contact(new_contact)
            action = "saved"
        
        # Show success message
        messagebox.showinfo(
            "Success",
            f"Emergency Contact {action} successfully!\n\n"
            f"Name: {name}\n"
            f"Phone Number: {phone_num}\n"
            f"Relationship: {relationship}\n"
            f"Email: {email}\n"
            f"Address: {address}\n"
            f"Primary: {'Yes' if primary else 'No'}"
        )
        
        # Reset form and update view
        self.reset_emergency_form()
        self.update_emergency_view()
        self.contact_manage.save_to_file()
    
    def clear_emergency_form(self):
        """Clear the contact form after confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the form?"):
            self.reset_emergency_form()
    
    def reset_emergency_form(self):
        """Reset the contact form to default values"""
        self.name_entry.delete(0, tk.END)
        self.phone_num_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.relationship_combo.set("Family")
        self.address_entry.delete("1.0", tk.END)
        self.primary_var.set(False)
        self.contact_manage.editing_contact_id = None
    
    def update_emergency_view(self):
        """Update the treeview with current contacts"""
        if not self.tree:
            return
        
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Define categories
        categories = ["Family", "Friend", "Emergency", "Travel Related"]
        
        # Add contacts by category
        for cat in categories:
            # Insert category node
            parent = self.tree.insert("", "end", text=cat, open=True, tags=("category",))
            
            # Get contacts for this category, sorted by primary first
            cat_contacts = sorted(
                [c for c in self.contact_manage.contacts if c.relationship == cat],
                key=lambda x: not x.primary  # Primary contacts first
            )
            
            # Insert contact nodes
            for contact in cat_contacts:
                self.tree.insert(parent, "end", iid=str(contact.id), values=(
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.address,
                    "✅" if contact.primary else ""
                ), tags=("contact",))
    
    def edit_selected_contact(self):
        """Edit the selected contact in the treeview"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Select Contact", "Please select a contact to edit.")
            return
        
        item_id = selected_item[0]
        
        # Check if a category was selected instead of a contact
        if not self.tree.parent(item_id):
            messagebox.showwarning("Invalid Section", "Please select a contact, not a category.")
            return
        
        # Get contact data
        contact_to_edit = self.contact_manage.get_contact(int(item_id))
        if contact_to_edit:
            # Populate form with contact data
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, contact_to_edit.name)
            
            self.phone_num_entry.delete(0, tk.END)
            self.phone_num_entry.insert(0, contact_to_edit.phone)
            
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, contact_to_edit.email)
            
            self.relationship_combo.set(contact_to_edit.relationship)
            
            self.address_entry.delete("1.0", tk.END)
            self.address_entry.insert("1.0", contact_to_edit.address)
            
            self.primary_var.set(contact_to_edit.primary)
            
            # Set editing mode
            self.contact_manage.editing_contact_id = contact_to_edit.id
    
    def delete_selected_contact(self):
        """Delete the selected contact from the treeview"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Select Contact", "Please select a contact to delete.")
            return
        
        item_id = selected_item[0]
        
        # Check if a category was selected instead of a contact
        if not self.tree.parent(item_id):
            messagebox.showwarning("Invalid Section", "Please select a contact, not a category.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
            return
        
        # Delete contact
        self.contact_manage.delete_contact(int(item_id))
        
        # Update view and save
        self.update_emergency_view()
        self.contact_manage.save_to_file()
        
        # Reset form if we were editing this contact
        if self.contact_manage.editing_contact_id == int(item_id):
            self.reset_emergency_form()
    
    def refresh(self):
        """Refresh the module (reload data and update view)"""
        self.contact_manage.load_from_file()
        self.update_emergency_view()
    
    def save_data(self):
        """Save contact data to file"""
        self.contact_manage.save_to_file()