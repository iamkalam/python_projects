import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from datetime import datetime
import re
from bson import ObjectId
from tkcalendar import DateEntry

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        # Set blackish background color and configure styles
        self.root.configure(bg="#121212")  # dark blackish background

        style = ttk.Style()
        style.theme_use('default')

        # Configure styles for ttk widgets to have dark background and light foreground
        style.configure("TFrame", background="#121212")
        style.configure("TLabel", background="#121212", foreground="#e0e0e0")
        style.configure("TLabelFrame", background="#121212", foreground="#ffffff")
        style.configure("TButton", background="#333333", foreground="#e0e0e0")
        style.map("TButton",
                  background=[('active', '#555555')],
                  foreground=[('active', '#ffffff')])
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="#e0e0e0",
                        fieldbackground="#1e1e1e")
        style.map("Treeview",
                  background=[('selected', '#4a90e2')],
                  foreground=[('selected', '#ffffff')])

        # Connect to MongoDB
        try:
            self.client = MongoClient('localhost', 27017)
            self.db = self.client['library_db']
            self.books_collection = self.db['books']
            self.lending_collection = self.db['lending_records']
            print("Connected to MongoDB successfully")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to MongoDB: {e}")
            root.quit()

        # Add heading label at the top
        self.heading_label = tk.Label(self.root, text="Library Management system BY Abdul Kalam 23p-0622",
                                      font=("Helvetica", 16, "bold"),
                                      bg="#121212", fg="#e0e0e0")
        self.heading_label.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.books_tab = ttk.Frame(self.notebook)
        self.lending_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.books_tab, text="Books Collection")
        self.notebook.add(self.lending_tab, text="Lending System")
        
        # Setup the UI for each tab
        self.setup_books_tab()
        self.setup_lending_tab()
        
        # Load initial data
        self.load_books()
        self.load_lending_records()
    
    def setup_books_tab(self):
        # Left frame for input form
        left_frame = ttk.LabelFrame(self.books_tab, text="Add Book")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right frame for book list
        right_frame = ttk.LabelFrame(self.books_tab, text="Books List")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.books_tab.columnconfigure(0, weight=1)
        self.books_tab.columnconfigure(1, weight=2)
        self.books_tab.rowconfigure(0, weight=1)
        
        # Form fields
        ttk.Label(left_frame, text="Title:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.title_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Author:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.author_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.author_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Genre:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.genre_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.genre_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Quantity:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.quantity_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.quantity_var,    width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Add, Update and Delete buttons
        ttk.Button(left_frame, text="Add Book", command=self.add_book).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(left_frame, text="Delete Selected", command=self.delete_book).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(left_frame, text="Clear Form", command=self.clear_book_form).grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(left_frame, text="View All Books", command=self.view_all_books).grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        # Book list treeview
        columns = ("Title", "Author", "Genre", "Quantity")
        self.books_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        # Set column headings
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind select event
        self.books_tree.bind('<<TreeviewSelect>>', self.on_book_select)
    
    def setup_lending_tab(self):
        # Left frame for lending form
        left_frame = ttk.LabelFrame(self.lending_tab, text="Lend Book")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right frame for lending records list
        right_frame = ttk.LabelFrame(self.lending_tab, text="Lending Records")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.lending_tab.columnconfigure(0, weight=1)
        self.lending_tab.columnconfigure(1, weight=2)
        self.lending_tab.rowconfigure(0, weight=1)
        
        # Form fields
        ttk.Label(left_frame, text="Book Title:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.lend_title_var = tk.StringVar()
        self.book_titles_combobox = ttk.Combobox(left_frame, textvariable=self.lend_title_var, width=30, state="readonly")
        self.book_titles_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Borrower Name:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.borrower_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.borrower_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Borrow Date:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.borrow_date_var = tk.StringVar()
        self.borrow_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.borrow_date_entry = DateEntry(left_frame, textvariable=self.borrow_date_var, date_pattern='yyyy-MM-dd', width=27)
        self.borrow_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Return Date:", font=("Helvetica", 12, "bold"), foreground="#ffffff").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.return_date_var = tk.StringVar()
        self.return_date_entry = DateEntry(left_frame, textvariable=self.return_date_var, date_pattern='yyyy-MM-dd', width=27)
        self.return_date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Add, Update and Delete buttons
        ttk.Button(left_frame, text="Lend Book", command=self.lend_book).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(left_frame, text="Update Return Date", command=self.update_return_date).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(left_frame, text="Delete Record", command=self.delete_lending_record).grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(left_frame, text="Clear Form", command=self.clear_lending_form).grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        # Lending records treeview
        columns = ("ID", "Book Title", "Borrower Name", "Borrow Date", "Return Date")
        self.lending_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        
        # Set column headings
        for col in columns:
            self.lending_tree.heading(col, text=col)
            if col == "ID":
                self.lending_tree.column(col, width=0, stretch=tk.NO)  # Hide ID column
            else:
                self.lending_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.lending_tree.yview)
        self.lending_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.lending_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind select event
        self.lending_tree.bind('<<TreeviewSelect>>', self.on_lending_select)
    
    def validate_date(self, date_string):
        """Validate date format YYYY-MM-DD"""
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not pattern.match(date_string):
            return False
        
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    

    def load_books(self):
        """Load books from database to the treeview"""
        # Clear existing items
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        # Fetch books from MongoDB
        books = self.books_collection.find()
        for book in books:
            self.books_tree.insert('', tk.END, values=(
                book['title'], 
                book['author'], 
                book['genre'], 
                book['quantity']
            ), tags=(str(book['_id']),))
        
        # Update the book titles in the lending combobox
        self.update_book_titles_combobox()

    def view_all_books(self):
        """View all books in the database by loading them and clearing the form"""
        self.load_books()
        self.clear_book_form()
    
    def update_book_titles_combobox(self):
        """Update the book titles in the lending combobox"""
        titles = [book['title'] for book in self.books_collection.find()]
        self.book_titles_combobox['values'] = titles
    
    def load_lending_records(self):
        """Load lending records from database to the treeview"""
        # Clear existing items
        for item in self.lending_tree.get_children():
            self.lending_tree.delete(item)
        
        # Fetch lending records from MongoDB
        records = self.lending_collection.find()
        for record in records:
            self.lending_tree.insert('', tk.END, values=(
                str(record['_id']),  # Store ObjectId as string
                record['book_title'],
                record['borrower_name'],
                record['borrow_date'],
                record['return_date']
            ))
    
    def add_book(self):
        """Add a new book to the database"""
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        genre = self.genre_var.get().strip()
        quantity = self.quantity_var.get().strip()
        
        # Validate input
        if not title or not author or not genre or not quantity:
            messagebox.showerror("Input Error", "All fields are required")
            return
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                messagebox.showerror("Input Error", "Quantity must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number")
            return
        
        # Check if book already exists
        existing_book = self.books_collection.find_one({"title": title, "author": author})
        if existing_book:
            # Update quantity instead of adding duplicate
            new_quantity = existing_book['quantity'] + quantity
            self.books_collection.update_one(
                {"_id": existing_book['_id']},
                {"$set": {"quantity": new_quantity}}
            )
            messagebox.showinfo("Success", f"Updated quantity of existing book '{title}' to {new_quantity}")
        else:
            # Insert new book
            self.books_collection.insert_one({
                "title": title,
                "author": author,
                "genre": genre,
                "quantity": quantity
            })
            messagebox.showinfo("Success", f"Book '{title}' added successfully")
        
        # Refresh the book list
        self.load_books()
        self.clear_book_form()
    
    def delete_book(self):
        """Delete selected book from the database"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a book to delete")
            return
        
        values = self.books_tree.item(selected, 'values')
        title = values[0]
        author = values[1]
        
        # Check if book is currently lent out
        lent_count = self.lending_collection.count_documents({"book_title": title})
        if lent_count > 0:
            messagebox.showerror("Delete Error", f"Cannot delete '{title}'. It has {lent_count} active lending records.")
            return
        
        # Delete the book
        result = self.books_collection.delete_one({"title": title, "author": author})
        if result.deleted_count > 0:
            messagebox.showinfo("Success", f"Book '{title}' deleted successfully")
            self.load_books()
        else:
            messagebox.showerror("Delete Error", "Failed to delete the book")
    
    def clear_book_form(self):
        """Clear the book form fields"""
        self.title_var.set("")
        self.author_var.set("")
        self.genre_var.set("")
        self.quantity_var.set("")
        self.books_tree.selection_remove(self.books_tree.selection())
    
    def on_book_select(self, event):
        """Handle book selection event"""
        selected = self.books_tree.selection()
        if selected:
            values = self.books_tree.item(selected, 'values')
            self.title_var.set(values[0])
            self.author_var.set(values[1])
            self.genre_var.set(values[2])
            self.quantity_var.set(values[3])
    
    def lend_book(self):
        """Lend a book to a borrower"""
        book_title = self.lend_title_var.get()
        borrower_name = self.borrower_var.get().strip()
        borrow_date = self.borrow_date_var.get().strip()
        return_date = self.return_date_var.get().strip()
        
        # Validate input
        if not book_title or not borrower_name:
            messagebox.showerror("Input Error", "Book title and borrower name are required")
            return
        
        if not self.validate_date(borrow_date) or not self.validate_date(return_date):
            messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Check if book exists and has available quantity
        book = self.books_collection.find_one({"title": book_title})
        if not book:
            messagebox.showerror("Book Error", f"Book '{book_title}' not found")
            return
        
        if book['quantity'] <= 0:
            messagebox.showerror("Book Error", f"No copies of '{book_title}' available")
            return
        
        # Insert lending record
        self.lending_collection.insert_one({
            "book_title": book_title,
            "borrower_name": borrower_name,
            "borrow_date": borrow_date,
            "return_date": return_date
        })
        
        # Update book quantity
        self.books_collection.update_one(
            {"_id": book['_id']},
            {"$set": {"quantity": book['quantity'] - 1}}
        )
        
        messagebox.showinfo("Success", f"Book '{book_title}' lent to {borrower_name}")
        
        # Refresh the lending records and books list
        self.load_lending_records()
        self.load_books()
        self.clear_lending_form()
    
    def update_return_date(self):
        """Update the return date of a lending record"""
        selected = self.lending_tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a lending record to update")
            return
        
        return_date = self.return_date_var.get().strip()
        if not self.validate_date(return_date):
            messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        values = self.lending_tree.item(selected, 'values')
        record_id = values[0]  # Get the stored ObjectId string
        
        try:
            # Update the record using the ObjectId
            result = self.lending_collection.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": {"return_date": return_date}}
            )
            
            if result.modified_count > 0:
                messagebox.showinfo("Success", "Return date updated successfully")
                self.load_lending_records()
            else:
                messagebox.showerror("Update Error", "Failed to update return date")
        except Exception as e:
            messagebox.showerror("Update Error", f"Error updating record: {e}")
    
    def delete_lending_record(self):
        """Delete a lending record and return the book to inventory"""
        selected = self.lending_tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a lending record to delete")
            return
        
        values = self.lending_tree.item(selected, 'values')
        record_id = values[0]  # Get the stored ObjectId string
        book_title = values[1]
        
        try:
            # Delete the record using the ObjectId
            result = self.lending_collection.delete_one({"_id": ObjectId(record_id)})
            
            if result.deleted_count > 0:
                # Update book quantity (add one back to inventory)
                book = self.books_collection.find_one({"title": book_title})
                if book:
                    self.books_collection.update_one(
                        {"_id": book['_id']},
                        {"$set": {"quantity": book['quantity'] + 1}}
                    )
                
                messagebox.showinfo("Success", f"Lending record deleted and '{book_title}' returned to inventory")
                
                # Refresh the lending records and books list
                self.load_lending_records()
                self.load_books()
                self.clear_lending_form()
            else:
                messagebox.showerror("Delete Error", "Failed to delete lending record")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Error deleting record: {e}")
    
    def clear_lending_form(self):
        """Clear the lending form fields"""
        self.lend_title_var.set("")
        self.borrower_var.set("")
        self.borrow_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.return_date_var.set("")
        if self.lending_tree.selection():
            self.lending_tree.selection_remove(self.lending_tree.selection())
    
    def on_lending_select(self, event):
        """Handle lending record selection event"""
        selected = self.lending_tree.selection()
        if selected:
            values = self.lending_tree.item(selected, 'values')
            # values[0] is the hidden ID column
            self.lend_title_var.set(values[1])
            self.borrower_var.set(values[2])
            self.borrow_date_var.set(values[3])
            self.return_date_var.set(values[4])

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()