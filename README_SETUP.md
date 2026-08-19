# Quick Project Setup

This guide explains how to install everything and run the project using [scripts/setup_and_run.sh](scripts/setup_and_run.sh).

## What the script does

1. Creates the virtual environment in py_home (if it does not exist).
2. Activates the virtual environment.
3. Upgrades pip, setuptools, and wheel.
4. Installs dependencies:
    - In MySQL mode: installs everything from [requirements.txt](requirements.txt).
    - In SQLite mode: skips mysqlclient automatically.
5. Creates .env from [.env.example](.env.example), if needed.
6. Sets DEBUG=True and local CSRF defaults for development.
7. Selects database automatically:
   - If MySQL is detected, it uses MySQL.
   - If MySQL is not detected, it uses SQLite.
8. In MySQL mode, creates the database and user with full privileges on that database.
9. Runs check and migrate.
10. Starts the Django server.

## Requirements

- Linux with bash
- Python 3.12+
- Optional: MySQL client/server (for MySQL mode)

## How to run

Default execution (automatic mode):

    bash scripts/setup_and_run.sh

Default server URL:
- http://127.0.0.1:8000

## Database options

Automatic (default):

    DB_MODE=auto bash scripts/setup_and_run.sh

Force MySQL:

    DB_MODE=mysql bash scripts/setup_and_run.sh

Force SQLite:

    DB_MODE=sqlite bash scripts/setup_and_run.sh

## Host and port configuration

    HOST=0.0.0.0 PORT=8001 bash scripts/setup_and_run.sh

## Useful variables

- DB_MODE: auto, mysql, sqlite
- PYTHON_BIN: python3, python3.12, etc.
- HOST: runserver host
- PORT: runserver port

## MySQL admin variables

By default, the script uses DB_USER and DB_PASSWORD as admin credentials to create database/user/permissions.

If needed, you can provide specific admin credentials:

    MYSQL_ADMIN_USER=root MYSQL_ADMIN_PASSWORD=your_password bash scripts/setup_and_run.sh

Other optional variables:
- MYSQL_ADMIN_HOST
- MYSQL_ADMIN_PORT
- DB_USER_HOST (default: localhost)

## What happens in MySQL mode

When DB_MODE is mysql, the script runs:

1. CREATE DATABASE IF NOT EXISTS
2. CREATE USER IF NOT EXISTS
3. ALTER USER (updates password)
4. GRANT ALL PRIVILEGES on the database
5. FLUSH PRIVILEGES

If it fails with current admin credentials, the script attempts a fallback to local root via sudo.

## Troubleshooting

1. MySQL connection error:
   - Confirm the MySQL service is running.
   - Confirm DB_HOST, DB_PORT, DB_USER, and DB_PASSWORD in .env.
2. mysql command not found:
   - Install MySQL client or use DB_MODE=sqlite.
3. mysqlclient error during pip install:
    - If you are using SQLite mode, run with DB_MODE=sqlite (mysqlclient is skipped).
    - If you are using MySQL mode, install system dependencies:
      - Ubuntu/Debian: sudo apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config
      - Fedora/RHEL: sudo dnf install -y python3-devel mysql-devel gcc pkgconfig
      - Arch: sudo pacman -S --needed python mysql-clients mariadb-libs base-devel pkgconf
4. Port already in use:
   - Use another port with PORT=8001.

## Related files

- [scripts/setup_and_run.sh](scripts/setup_and_run.sh)
- [.env.example](.env.example)
- [casa/settings.py](casa/settings.py)
- [README.md](README.md)
