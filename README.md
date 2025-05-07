# Maktab_Final
this is a repo for maktab Sharif Final Project (DRF)
Online Shop Project
Description
This project is an online store built with Django, allowing vendors to manage products and their own staff ,customers to browse and purchase them. The project includes features such as staff panel, user panels, product categories, shopping cart, and order management.

Features
Staff panel for managing staffs by their manager, managing products, orders
User panel for managing their addresses, orders
Cart with real-time updates.
User registration and authentication (via email and phone)
Admin panel for managing the overall store.
OTP authentication
Technologies
Backend: Python/Django
Frontend: HTML, CSS, Bootstrap, jQuery
Database: SQLite (for development)
Installation
1.Clone the repository:

   git clone https://github.com/behradsh/Maktab_Final
2.Change to the project directory:

   cd project_directory
3.Create a virtual environment:

    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
4.Install dependencies:

     pip install -r requirements.txt
5.Set up the database: -- For development, use SQLite (default) -- For production, configure PostgreSQL using .env file
6.Run migrations:

    python manage.py migrate
7.Create a superuser for the admin panel:

    python manage.py createsuperuser
8.Run the development server:

    python manage.py runserver
