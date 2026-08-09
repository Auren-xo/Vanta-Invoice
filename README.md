# Danpa Invoice Manager

A modern invoice management dashboard built with **HTML, CSS, JavaScript, and Node.js**, with a **Python/FastAPI + PostgreSQL backend** for structured data management.

Danpa allows users to create and manage invoices, calculate totals dynamically, update invoice statuses, and interact with a responsive dashboard designed for a clean, professional invoicing experience.

## 🔗 Live Demo

**[View Danpa Invoice Manager](https://danpa-invoice.netlify.app/)**

## ✨ Features

* Create and manage invoices
* Dynamic invoice item calculations
* Automatic subtotal and total calculation
* Client information management
* Generate and download invoices as PDF
* Invoice status management

  * Draft
  * Sent
  * Paid
  * Overdue
* Invoice due dates and payment terms
* Notes and additional invoice information
* Responsive dashboard interface
* Search and interactive UI components
* Persistent invoice data
* PostgreSQL database integration
* REST API for invoice operations

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript (ES Modules)
* Responsive CSS Grid and Flexbox

### Backend

* Node.js
* Node.js HTTP server
* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Database

* PostgreSQL

### Other Tools

* Git & GitHub
* Environment variables with `.env`
* Python virtual environment (`.venv`)

## 📁 Project Structure

```text
Danpa Invoice Manager/
├── backend-python/
│   └── main.py
├── data/
├── index.html
├── styles.css
├── data.css
├── interactions.css
├── interactions.js
├── app.js
├── server.js
├── package.json
├── .env.example
└── README.md
```

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Auren-xo/Vanta-Invoice.git
cd Danpa-Invoice-Manager
```

### 2. Install Node.js dependencies

```bash
npm install
```

### 3. Set up the environment

Create a `.env` file based on `.env.example` and add your PostgreSQL database connection details.

### 4. Set up the Python environment

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install the Python dependencies required by the backend.

### 5. Start the application

```bash
npm start
```

The application will run locally through the Node.js server.

## 🔌 API

The application provides invoice-related API endpoints including:

```text
GET    /api/invoices
POST   /api/invoices
PATCH  /api/invoices/:id/status
GET    /api/health
```

These endpoints handle retrieving invoices, creating new invoices, updating invoice statuses, and checking the API/database health.

## 📱 Responsive Design

Danpa is designed to adapt across desktop, tablet, and mobile screen sizes using responsive CSS layouts and media queries.

## 🎯 Project Purpose

Danpa Invoice Manager was built as a portfolio project to demonstrate practical frontend development, API integration, backend development, database interaction, and responsive UI implementation in a real-world application.

## 👩🏽‍💻 Author

**Auren-xo**

Software Developer

GitHub: [Auren-xo](https://github.com/Auren-xo)
