# 🛒 CommerceHub — Production-Ready E-Commerce REST API

CommerceHub is a **production-ready E-Commerce REST API** built with **Django REST Framework**.

The project provides a complete e-commerce backend including authentication, role-based authorization, product and category management, shopping cart, wishlist, order processing, payments, reviews, asynchronous tasks, automated testing, Docker-based infrastructure, CI/CD, API documentation, and cloud deployment.

---

## 🚀 Live Demo

### 🌐 Live API

https://commercehub-api-hst9.onrender.com/

### 📚 Swagger Documentation

https://commercehub-api-hst9.onrender.com/api/docs/

### 📖 ReDoc Documentation

https://commercehub-api-hst9.onrender.com/api/redoc/

---

## ✨ Key Features

* Custom User Authentication
* Customer / Seller / Admin Roles
* JWT Authentication
* Email Verification
* Password Reset
* Product Management
* Category Management
* Shopping Cart
* Wishlist
* Order Processing
* Stock Management
* Payment Management
* Product Reviews
* Role-Based Permissions
* PostgreSQL Database
* Redis
* Celery Background Tasks
* Docker & Docker Compose
* Nginx Reverse Proxy
* Gunicorn
* Automated Testing
* 97% Test Coverage
* GitHub Actions CI
* OpenAPI / Swagger Documentation
* Production Deployment on Render

---

# 🏗️ Technology Stack

## Backend

* Python 3.11
* Django
* Django REST Framework
* Simple JWT
* drf-spectacular
* django-filter

## Database

* PostgreSQL
* pgAdmin

## Background Processing

* Celery
* Redis

## Web Server / Infrastructure

* Gunicorn
* Nginx
* Docker
* Docker Compose

## Testing

* Pytest
* pytest-django
* Coverage

## CI/CD

* GitHub Actions

## Deployment

* Render
* Render PostgreSQL
* Upstash Redis

## Email

* Gmail SMTP
* Celery asynchronous email processing

---

# 👤 Authentication & Users

CommerceHub includes a custom user system with role-based access control.

### Features

* Custom User Model
* `AUTH_USER_MODEL`
* Customer role
* Seller role
* Admin role
* Password hashing
* User registration
* JWT login
* Access token
* Refresh token
* Protected endpoints
* Profile update
* Email verification
* Verification token
* Resend verification email
* Forgot password
* Password reset
* Password reset token
* Password update
* Gmail SMTP
* HTML verification email

### Authentication Flow

```text
Register
   ↓
Email Verification
   ↓
Login
   ↓
Access Token
   ↓
Protected API
```

JWT authentication is used to protect private API endpoints.

---

# 📂 Categories

Category management supports role-based permissions.

### Features

* Category model
* Category CRUD
* Public category listing
* Admin-only create
* Admin-only update
* Admin-only delete
* Authentication
* Permission validation

### Demo Data

```text
10 Categories
```

---

# 📦 Products

CommerceHub provides complete product management functionality.

### Features

* Product model
* Seller ownership
* Category relationship
* Product image upload
* Stock management
* Product creation
* Product listing
* Product detail
* Product update
* Product deletion
* Pagination
* Search
* Filtering
* Ordering
* Seller permissions
* Admin management

### Demo Data

```text
10 Products
```

---

# 🛒 Shopping Cart

The cart system allows customers to manage products before creating an order.

### Features

* User-specific cart
* Cart items
* Add product
* Update quantity
* Remove product
* Duplicate prevention
* Stock validation
* Quantity validation
* Automatic cart total
* Authentication
* Permission control

### Cart Flow

```text
Product
   ↓
Add to Cart
   ↓
Update Quantity
   ↓
Calculate Total
   ↓
Create Order
```

---

# ❤️ Wishlist

Customers can save products for later.

### Features

* Wishlist model
* Add product
* Remove product
* View wishlist
* Update functionality
* Authentication
* Permissions

---

# 📦 Orders

The order system handles the complete purchase workflow.

### Features

* Order model
* OrderItem model
* Cart → Order conversion
* Automatic total calculation
* Order items
* Stock deduction
* Cart clearing
* Order cancellation
* Stock restoration
* Cancelled-order protection
* Customer authorization
* Seller management
* Admin management
* Atomic database transactions
* Transaction-safe stock handling

---

## 🔄 Order Status

CommerceHub supports the following order states:

```text
PENDING
   ↓
CONFIRMED
   ↓
PROCESSING
   ↓
SHIPPED
   ↓
DELIVERED
```

Orders can also be cancelled:

```text
PENDING / CONFIRMED / PROCESSING
              ↓
          CANCELLED
```

Invalid status transitions are protected by business logic.

---

# 💳 Payments

The payment system is connected directly to orders.

### Features

* Payment model
* Order ↔ Payment OneToOne relationship
* Transaction ID
* Payment methods
* Payment statuses
* Payment creation
* Duplicate payment prevention
* Cancelled-order protection
* Payment status transition rules
* Refund support
* Customer authorization
* Admin authorization

### Supported Payment Method Example

```text
CARD
```

### Payment Statuses

```text
PENDING
SUCCESS
FAILED
REFUNDED
```

---

# ⭐ Reviews

Customers can review products after completing a purchase.

### Features

* Review CRUD
* Customer-only review creation
* Product reviews
* Purchased-product validation
* Delivered-order validation
* Duplicate review prevention
* Rating validation
* 1–5 rating system
* Authentication
* Permission control

Example permission response:

```json
{
  "detail": "Only customers can create reviews."
}
```

This demonstrates that role-based permissions are actively enforced.

---

# 📚 API Documentation

CommerceHub uses **drf-spectacular** to generate OpenAPI documentation.

### Swagger UI

https://commercehub-api-hst9.onrender.com/api/docs/

Swagger provides:

* Interactive API testing
* Endpoint documentation
* Request schemas
* Response schemas
* Authentication
* API tags
* Order status enums
* Payment status enums

### ReDoc

https://commercehub-api-hst9.onrender.com/api/redoc/

### OpenAPI Schema

```text
/api/schema/
```

---

# 🏠 API Health Check

The root endpoint provides a simple health response.

### Endpoint

```http
GET /
```

### Example Response

```json
{
  "message": "CommerceHub API is running",
  "documentation": "/api/docs/",
  "status": "healthy"
}
```

Live endpoint:

https://commercehub-api-hst9.onrender.com/

---

# 🏗️ System Architecture

```text
                    ┌────────────────────┐
                    │      Client        │
                    │ Swagger / Postman  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │       Nginx        │
                    │   Reverse Proxy    │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │      Gunicorn      │
                    │       Django       │
                    │        DRF         │
                    └───────┬───────┬────┘
                            │       │
                ┌───────────┘       └────────────┐
                ▼                                ▼
       ┌──────────────────┐             ┌──────────────────┐
       │    PostgreSQL    │             │      Redis       │
       │     Database     │             │   Message Broker │
       └──────────────────┘             └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │      Celery      │
                                        │ Background Tasks │
                                        └──────────────────┘
```

---

# 🗄️ Database Relationships

Main entities include:

```text
User
 │
 ├── Cart
 │     └── CartItem
 │            └── Product
 │
 ├── Wishlist
 │
 ├── Order
 │     └── OrderItem
 │            └── Product
 │
 └── Review
        └── Product

Category
   │
   └── Product

Order
   │
   └── Payment
```

---

# 🔐 Security

CommerceHub implements multiple security practices.

### Authentication

* JWT authentication
* Access tokens
* Refresh tokens
* Protected endpoints

### Authorization

* Customer permissions
* Seller permissions
* Admin permissions
* Object-level ownership checks

### Application Security

* Password hashing
* Environment-based secrets
* `DEBUG=False` in production
* `ALLOWED_HOSTS`
* `CSRF_TRUSTED_ORIGINS`
* Database credentials through environment variables
* Transaction-safe operations
* Stock validation
* Duplicate transaction prevention

Sensitive credentials are not stored in the repository.

---

# 🐳 Docker

The project includes production-oriented Docker configuration.

### Main Docker Files

```text
Dockerfile.prod
docker-compose.prod.yml
.dockerignore
```

### Production Services

```text
Django / Gunicorn
PostgreSQL
Redis
Celery
Nginx
```

### Build & Run

```bash
docker compose -f docker-compose.prod.yml up --build
```

### Check Services

```bash
docker compose -f docker-compose.prod.yml ps
```

---

# ⚙️ Celery & Redis

Celery is used for asynchronous background processing.

Redis is used as the message broker and result backend.

### Architecture

```text
Django
   ↓
Redis
   ↓
Celery Worker
   ↓
Background Task
```

Use cases include asynchronous email processing and other background operations.

---

# 📧 Email System

CommerceHub supports:

* Email verification
* Resend verification email
* Forgot password
* Password reset
* HTML emails
* Gmail SMTP
* Celery-based asynchronous email processing

### Local

```text
Gmail SMTP          ✅
Email Verification  ✅
Celery              ✅
```

### Production

```text
SMTP Configuration  ✅
Email Configuration ✅
Celery Worker       🟡 Final production setup
```

---

# 🧪 Testing

CommerceHub has a comprehensive automated test suite.

## Final Test Result

```text
187 passed
0 failed
97% coverage
```

### Tested Modules

```text
Users          ✅
Categories     ✅
Products       ✅
Cart           ✅
Wishlist       ✅
Orders         ✅
Payments       ✅
Reviews        ✅
```

Tests have also been executed successfully inside the Docker environment.

---

# 📊 Test Coverage

```text
Test Cases       : 187
Passed           : 187
Failed           : 0
Coverage         : 97%
```

This provides strong confidence in the core business logic and API behavior.

---

# ⚙️ GitHub Actions CI

The project uses GitHub Actions for automated validation.

### CI Pipeline

```text
Git Push
   ↓
GitHub Actions
   ↓
Python 3.11
   ↓
PostgreSQL
   ↓
Redis
   ↓
Django Check
   ↓
Database Migrations
   ↓
Pytest
   ↓
SUCCESS
```

The CI pipeline validates the application automatically after code changes.

---

# 🌐 Nginx + Gunicorn

Production request architecture:

```text
Client
   ↓
Nginx :8080
   ↓
Gunicorn :8000
   ↓
Django
```

Nginx is responsible for reverse proxying and static file serving.

Gunicorn serves the Django application.

---

# 📁 Static Files

Production static file configuration includes:

* `STATIC_URL`
* `STATIC_ROOT`
* `collectstatic`
* Static volume
* Nginx static serving

Static files have been verified in the production environment.

Example:

```text
admin/css/base.css
```

---

# 🚀 Production Deployment

CommerceHub is deployed on **Render** using a Docker-based production environment.

### Production Components

```text
Render
├── Django / Gunicorn
├── PostgreSQL
└── Redis
```

The application is configured with:

```text
DEBUG=False
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
SECRET_KEY
Database Environment Variables
Redis Environment Variables
SMTP Environment Variables
```

---

# 🗄️ Production Database

Production PostgreSQL configuration includes:

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

Database migrations are executed during deployment.

---

# 🧪 API Testing Workflow

The API can be tested through:

* Swagger UI
* Postman
* Automated Pytest tests

Typical customer workflow:

```text
Register
   ↓
Email Verification
   ↓
Login
   ↓
Receive JWT
   ↓
Browse Categories
   ↓
Browse Products
   ↓
Add Product to Cart
   ↓
Update Quantity
   ↓
Create Order
   ↓
Payment
   ↓
Order Processing
   ↓
Delivery
   ↓
Product Review
```

---

# 📊 Demo Data

Demo data has been created for API demonstration and portfolio testing.

```text
Categories       10
Products         10
Orders           Demo
Payments         Demo
Reviews          Customer-based testing
```

Demo data is used only for showcasing and testing the API.

---

# 🚀 Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CommerceHub.git
cd CommerceHub
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=commercehub
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Never commit real credentials or `.env` files to GitHub.

---

# 🗃️ Database Setup

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

---

# 📦 Static Files

Run:

```bash
python manage.py collectstatic --noinput
```

---

# ▶️ Run Development Server

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

---

# 🧪 Run Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=.
```

Generate HTML coverage report:

```bash
coverage html
```

---

# 📁 Project Structure

```text
CommerceHub/
│
├── src/
│   ├── users/
│   ├── products/
│   ├── categories/
│   ├── cart/
│   ├── wishlist/
│   ├── orders/
│   ├── payments/
│   ├── reviews/
│   │
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
│
├── Dockerfile.prod
├── docker-compose.prod.yml
├── .dockerignore
├── .gitignore
├── requirements.txt
├── manage.py
└── README.md
```

---

# 📌 API Endpoints

Main API sections:

```text
/api/users/
/api/categories/
/api/products/
/api/cart/
/api/wishlist/
/api/orders/
/api/payments/
/api/reviews/
```

Documentation:

```text
/api/docs/
/api/redoc/
/api/schema/
```

---

# 📈 Project Status

| Component                | Status                |
| ------------------------ | --------------------- |
| Custom User Model        | ✅ Complete            |
| Authentication           | ✅ Complete            |
| JWT                      | ✅ Complete            |
| Email Verification       | ✅ Complete            |
| Password Reset           | ✅ Complete            |
| Categories               | ✅ Complete            |
| Products                 | ✅ Complete            |
| Cart                     | ✅ Complete            |
| Wishlist                 | ✅ Complete            |
| Orders                   | ✅ Complete            |
| Payments                 | ✅ Complete            |
| Reviews                  | ✅ Complete            |
| PostgreSQL               | ✅ Complete            |
| Redis                    | ✅ Complete            |
| Celery Code              | ✅ Complete            |
| API Documentation        | ✅ Complete            |
| Automated Testing        | ✅ Complete            |
| 187 Tests                | ✅ Passed              |
| 97% Coverage             | ✅ Complete            |
| Docker                   | ✅ Complete            |
| Nginx                    | ✅ Complete            |
| Gunicorn                 | ✅ Complete            |
| GitHub Actions CI        | ✅ Complete            |
| Production Deployment    | 🟢 Live               |
| Production Email         | 🟡 Final Verification |
| Production Celery Worker | 🟡 Finalization       |
| Final Live E2E Test      | 🟡 Finalization       |

---

# 🎯 Current Finalization Tasks

The core feature development is complete.

Remaining production finalization:

```text
1. Production Celery Worker
2. Production verification email test
3. Live email verification
4. Verified customer JWT login
5. Final live API smoke test
6. Users migration warning cleanup
```

No additional core feature development is required for the current portfolio version.

---

# 🔮 Future Improvements

Potential future enhancements:

* Stripe / payment gateway integration
* Advanced inventory management
* Order tracking
* Seller dashboard
* Admin analytics dashboard
* Product recommendation system
* Advanced search
* API rate limiting
* Response caching
* Monitoring with Prometheus
* Grafana dashboards
* Automated production deployment

These are optional future improvements and are not required for the current core e-commerce API.

---

# 🏆 Project Highlights

CommerceHub demonstrates practical backend engineering across the full development lifecycle:

```text
REST API Design
        ↓
Authentication
        ↓
Authorization
        ↓
Database Design
        ↓
Business Logic
        ↓
Transactions
        ↓
Stock Management
        ↓
Payments
        ↓
Background Tasks
        ↓
Automated Testing
        ↓
Docker
        ↓
CI/CD
        ↓
Production Deployment
```

### Key Metrics

```text
187 Tests Passed
97% Test Coverage
8 Core API Modules
JWT Authentication
PostgreSQL
Redis
Celery
Docker
Nginx
Gunicorn
GitHub Actions
Swagger / OpenAPI
Production Deployment
```

---

# 👨‍💻 Author

## Almas Hossen

Python Backend Developer

### Technical Focus

```text
Python
Django
Django REST Framework
FastAPI
PostgreSQL
REST APIs
Docker
Celery
Redis
Backend Development
```

---

# 📜 License

This project is created for portfolio and educational purposes.
