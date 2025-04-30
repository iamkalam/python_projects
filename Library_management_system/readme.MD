
# Library Management System

A desktop application for managing a library's book collection and lending system. Built with Python, Tkinter for the GUI, and MongoDB as the backend database. The application features a dark-themed interface and provides functionalities to add, view, update, and delete books, as well as manage lending records.

## Features

- Add new books with details such as title, author, genre, and quantity.
- View all books in the collection.
- Delete books (only if they are not currently lent out).
- Lend books to borrowers with borrow and return dates.
- Update return dates for lending records.
- Delete lending records and automatically update book inventory.
- User-friendly dark-themed interface with tabbed navigation.

## Technologies Used

- Python 3
- Tkinter (GUI framework)
- pymongo (MongoDB driver for Python)
- tkcalendar (Date picker widget for Tkinter)
- MongoDB (NoSQL database)

## Installation

1. Ensure you have Python 3 installed on your system.
2. Install MongoDB and make sure it is running locally on the default port (27017).
3. Install required Python packages using pip:

```bash
pip install pymongo tkcalendar
```

## Usage

1. Clone or download the project files.
2. Ensure MongoDB is running locally.
3. Run the application:

```bash
python Task1.py
```

4. The application window will open with two tabs: "Books Collection" and "Lending System".
5. Use the "Books Collection" tab to add, view, and delete books.
6. Use the "Lending System" tab to lend books, update return dates, and manage lending records.

## UI Overview

- **Books Collection Tab**: Form on the left to add new books and buttons to add, delete, clear form, and view all books. The right side displays the list of books.
- **Lending System Tab**: Form on the left to lend books and update return dates. The right side displays lending records.

## Author

Abdul Kalam (23p-0622)
