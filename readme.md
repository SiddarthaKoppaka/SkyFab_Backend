# Skyfab Backend REST API

## 🚀 Overview
This is the backend API for the **Skyfab** e-commerce platform. It provides endpoints for **user authentication, product management, cart operations, and order processing**.

This project is built with **Django REST Framework (DRF)** and is designed to be containerized using **Docker**.

---

## 📌 Features
- **User Authentication**: Register, login, profile management, password reset
- **Product Management**: View, search, filter products
- **Cart System**: Add/remove items, manage cart
- **Order Processing**: Place orders, view order history
- **API Documentation**: Swagger, ReDoc, and DRF Browsable API
- **Containerized Deployment**: Supports Docker & Docker Compose

---

## 🛠️ Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/skyfab-backend.git
cd skyfab-backend
```

### **2️⃣ Create a Virtual Environment (Optional)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Run Database Migrations**
```bash
python manage.py migrate
```

### **5️⃣ Start the Development Server**
```bash
python manage.py runserver
```

Now visit `http://127.0.0.1:8000/` to access the API.

---

## 📦 Docker Deployment

### **1️⃣ Build the Docker Image**
```bash
docker build -t skyfab-backend .
```

### **2️⃣ Run the Application in a Container**
```bash
docker run -p 8000:8000 skyfab-backend
```

### **3️⃣ Using Docker Compose**
Run the following command to start the **API, database, and dependencies**:
```bash
docker-compose up -d
```

---

## 📜 API Documentation

### **Swagger UI** (Interactive API Testing)
```
http://127.0.0.1:8000/api/docs/swagger/
```

### **ReDoc** (Modern API Documentation)
```
http://127.0.0.1:8000/api/docs/redoc/
```

### **DRF Browsable API**
```
http://127.0.0.1:8000/api/docs/
```

### **OpenAPI JSON Schema**
```
http://127.0.0.1:8000/api/schema/
```

---

## 🔑 Environment Variables
Create a `.env` file and configure the following:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@db:5432/skyfab
ALLOWED_HOSTS=*
```

---

## 📜 API Endpoints

### **User Authentication**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/v1/users/register/` | Register a new user |
| `POST` | `/api/v1/users/login/` | Login user & get tokens |
| `POST` | `/api/v1/users/logout/` | Logout user |
| `POST` | `/api/v1/users/forgot-password/` | Reset password |

### **Products**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/api/v1/products/` | List all products |
| `GET` | `/api/v1/products/?search=term` | Search products |

### **Cart & Orders**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/v1/cart/add/` | Add product to cart |
| `POST` | `/api/v1/orders/place/` | Place an order |

---

## 🏗️ Docker Compose Setup

Create a **docker-compose.yml** file in the project root:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

  db:
    image: postgres:13
    restart: always
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: skyfab
    ports:
      - "5432:5432"
```

---

## ✅ Running Tests
To run tests using `pytest`:
```bash
pytest
```

---

## 🚀 Conclusion
This repository is ready for production deployment and is **fully containerized** with Docker. Follow the instructions to run the API locally or deploy it using **Docker Compose**.

---

## 💬 Support
For any issues, contact **support@skyfab.com** or create an issue in the repository.

🔥 **Happy Coding!** 🚀