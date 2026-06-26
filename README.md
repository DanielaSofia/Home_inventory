# Home Inventory

A comprehensive Django application for managing household inventory, pantry items, shopping lists, and expenses.

## Table of Contents

- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [API Setup & Testing](#api-setup--testing)
- [Security Features](#security-features)
- [Common Commands](#common-commands)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Activate the virtual environment
source py_home/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 4. Apply database migrations
python manage.py migrate

# 5. Create a superuser (for admin access)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Requirements

- **Python** 3.12+
- **MySQL** 5.7+ or **MariaDB** 10.3+
- **Git** (for cloning and version control)
- Virtual environment (already provided at `py_home/`)

## Installation

### Step 1: Activate the Virtual Environment

The project includes a pre-configured Python virtual environment:

```bash
source py_home/bin/activate
```

**Verify activation:**
```bash
which python
# Should show: /path/to/Home_inventory/py_home/bin/python
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- Django 6.0.6
- Django REST Framework 3.17.1
- MySQLclient 2.2.8
- Pillow 12.2.0
- pytest 9.1.1 (for testing)
- And other utilities

### Step 3: Verify Installation

```bash
python manage.py check
```

This command validates your Django configuration. You should see:
```
System check identified no issues (0 silenced).
```

## Environment Configuration

### Creating the `.env` File

The application uses environment variables for sensitive configuration. Create your `.env` file from the template:

```bash
cp .env.example .env
```

### Configuration Variables

Edit `.env` and configure these variables:

| Variable | Example | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `your-secret-key-here` | Django secret key (must be unique and kept secret) |
| `DEBUG` | `False` | Debug mode (always `False` in production) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames |
| `DB_ENGINE` | `django.db.backends.mysql` | Database backend |
| `DB_NAME` | `casa_inventory` | Database name |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | `password123` | Database password |
| `DB_HOST` | `localhost` | Database hostname/IP |
| `DB_PORT` | `3306` | Database port |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Comma-separated trusted origins for CSRF |

### Example `.env` for Local Development

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=casa_inventory
DB_USER=root
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Security Note

**⚠️ Important:**
- Never commit `.env` to version control (it's already in `.gitignore`)
- Never share your `.env` file
- Generate a strong `SECRET_KEY` for production

## Database Setup

### 1. Install MySQL

```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo mysql_secure_installation
```

Start MySQL service:
```bash
sudo systemctl start mysql
sudo systemctl enable mysql  # Enable auto-start on boot
```

Verify MySQL is running:
```bash
sudo systemctl status mysql
```

### 2. Create Database and User

Connect to MySQL:
```bash
mysql -u root -p
```

Create the database and user:
```sql
CREATE DATABASE casa_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'casa_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON casa_inventory.* TO 'casa_user'@'localhost';
FLUSH PRIVILEGES;
exit;
```

### 3. Import Database Schema

```bash
# Import schema structure
mysql -u root -p casa_inventory < casa_struct.sql

# Import sample data (optional)
mysql -u root -p casa_inventory < dados.sql
```

### 4. Update `.env` with Database Credentials

Update your `.env` file:

```env
DB_USER=casa_user
DB_PASSWORD=secure_password_here
DB_NAME=casa_inventory
DB_HOST=localhost
DB_PORT=3306
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

This creates all necessary Django tables (auth, sessions, tokens, etc.).

## API Setup & Testing

### Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Access the Admin Panel

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

### Generate API Authentication Token

The API uses token-based authentication. To get a token:

**Via Admin Panel:**
1. Go to `/admin/authtoken/token/`
2. Click "Add Token"
3. Select your user and save

**Via API:**
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Response:
```json
{
  "token": "abc123def456..."
}
```

### Test API Endpoints

**List all items:**
```bash
curl -X GET http://localhost:8000/api/itens/ \
  -H "Authorization: Token abc123def456..."
```

**List all divisions:**
```bash
curl -X GET http://localhost:8000/api/divisoes/ \
  -H "Authorization: Token abc123def456..."
```

**Available Endpoints:**
- `GET/POST /api/divisoes/` — Manage divisions
- `GET/POST /api/itens/` — Manage items
- `GET/POST /api/desejos/` — Manage wishlist
- `GET/POST /api/compras/` — Manage shopping list
- `GET/POST /api/consumiveis/` — Manage pantry items
- `GET /api/historico-compras/` — View purchase history

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test class
pytest casa/inventory/tests.py::TestItemViewSet -v

# Run with coverage report
pytest --cov=casa.inventory
```

**Note:** Tests require proper database configuration in `.env`

## Security Features

The project implements multiple security best practices:

- ✅ **Environment-based Secrets** — All sensitive data in `.env` (not in code)
- ✅ **CSRF Protection** — Cross-Site Request Forgery prevention enabled
- ✅ **Secure Cookies** — Session and CSRF cookies marked secure
- ✅ **Security Headers** — XFrame, CSP, and HSTS headers configured
- ✅ **Token Authentication** — API requires authentication tokens
- ✅ **Permission Classes** — API endpoints require authentication
- ✅ **SQL Injection Prevention** — Django ORM prevents SQL injection
- ✅ **SSL/HTTPS** — Automatic redirect to HTTPS in production

**Production Requirements:**
- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Enable `SECURE_SSL_REDIRECT=True`
- Configure `ALLOWED_HOSTS` properly
- Use HTTPS certificates

## Common Commands

```bash
# Start development server
python manage.py runserver

# Create database tables
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser account
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Run all tests
pytest

# Run tests with coverage
pytest --cov=casa.inventory

# Check for unmigrated changes
scripts/check_migrations.sh
```

## Project Structure

```
Home_inventory/
├── casa/
│   ├── settings.py              # Django configuration (uses .env)
│   ├── urls.py                  # Main URL router
│   ├── wsgi.py                  # WSGI entry point
│   ├── logging_config.py        # Centralized logging setup
│   └── inventory/               # Main app
│       ├── models.py            # Database models
│       ├── views.py             # Web views
│       ├── views_api.py         # REST API ViewSets
│       ├── serializers.py       # API serializers
│       ├── forms.py             # Django forms
│       ├── admin.py             # Django admin configuration
│       ├── urls.py              # App URL routing
│       ├── tests.py             # Test suite (pytest)
│       ├── migrations/          # Database migrations
│       ├── templates/           # HTML templates
│       └── static/              # CSS, JavaScript, images
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── manage.py                    # Django management CLI
├── requirements.txt             # Python dependencies
├── pytest.ini                   # pytest configuration
├── casa_struct.sql              # Database schema
├── dados.sql                    # Sample data
├── README.md                    # This file
└── py_home/                     # Virtual environment

```

## Deployment

### Pre-Deployment Checklist

Before deploying to production:

```bash
# 1. Update settings in .env
DEBUG=False                          # Disable debug mode
SECRET_KEY=<generate-new-key>        # Generate secure key
ALLOWED_HOSTS=yourdomain.com         # Set your domain
CSRF_TRUSTED_ORIGINS=https://...    # Set HTTPS origin

# 2. Collect static files
python manage.py collectstatic

# 3. Run security checks
python manage.py check --deploy

# 4. Run migrations on production database
python manage.py migrate

# 5. Test API locally first
python manage.py runserver 0.0.0.0:8000
```

### Using Gunicorn

```bash
# Install Gunicorn (if not in requirements.txt)
pip install gunicorn

# Run Gunicorn
gunicorn casa.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With Gunicorn control script
./gunicorn.ctl start
```

## Troubleshooting

### MySQL Connection Error

```
django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'localhost'")
```

**Solution:**
- Verify MySQL is running: `sudo systemctl status mysql`
- Check `.env` database credentials match your MySQL user
- Verify user has permissions: `GRANT ALL PRIVILEGES ON casa_inventory.* TO 'user'@'localhost';`

### Database Already Exists Error

```
Error: Database already exists
```

**Solution:**
```bash
# Drop existing database (WARNING: loses data)
mysql -u root -p -e "DROP DATABASE casa_inventory;"

# Re-create database
mysql -u root -p casa_inventory < casa_struct.sql

# Run migrations
python manage.py migrate
```

### ModuleNotFoundError: No module named 'django'

**Solution:**
```bash
# Ensure virtual environment is activated
source py_home/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Denied on Linux

```
Permission denied: 'py_home/bin/python'
```

**Solution:**
```bash
chmod +x py_home/bin/python
chmod +x py_home/bin/activate
```

### Port 8000 Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Run on different port
python manage.py runserver 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

## License

This project is for personal use. Please refer to LICENSE file for details.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Django/DRF documentation
3. Create an issue in the repository
