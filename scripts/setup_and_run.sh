#!/usr/bin/env bash
set -euo pipefail

# Bootstrap local development environment and run Django server.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/py_home"
ENV_FILE="$ROOT_DIR/.env"
ENV_EXAMPLE="$ROOT_DIR/.env.example"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
DB_MODE="${DB_MODE:-auto}"

get_env_value() {
  local key="$1"
  local value

  value="$(grep -E "^${key}=" "$ENV_FILE" | head -n 1 | cut -d '=' -f2- || true)"
  echo "$value"
}

sql_escape() {
  printf "%s" "$1" | sed "s/'/''/g"
}

sql_ident_escape() {
  printf "%s" "$1" | sed 's/`/``/g'
}

run_mysql_admin_sql() {
  local sql="$1"
  local admin_user="$2"
  local admin_password="$3"
  local admin_host="$4"
  local admin_port="$5"
  local admin_args=("-h" "$admin_host" "-P" "$admin_port" "-u" "$admin_user")

  if [ -n "$admin_password" ]; then
    if MYSQL_PWD="$admin_password" mysql "${admin_args[@]}" -e "$sql"; then
      return 0
    fi
  else
    if mysql "${admin_args[@]}" -e "$sql"; then
      return 0
    fi
  fi

  if [ "$admin_user" = "root" ] && command -v sudo >/dev/null 2>&1; then
    if sudo mysql -e "$sql"; then
      return 0
    fi
  fi

  return 1
}

echo "[1/6] Indo para a raiz do projeto..."
cd "$ROOT_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERRO: $PYTHON_BIN nao encontrado. Instale Python 3.12+ e tente novamente." >&2
  exit 1
fi

echo "[2/6] Configurando virtualenv em $VENV_DIR..."
if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[3/6] Atualizando ferramentas de instalacao..."
python -m pip install --upgrade pip setuptools wheel

if [ "$DB_MODE" = "auto" ]; then
  if command -v mysql >/dev/null 2>&1; then
    DB_MODE="mysql"
    echo "MySQL detectado no sistema. Usando MySQL por padrao."
  else
    DB_MODE="sqlite"
    echo "MySQL nao detectado. Usando SQLite por padrao."
  fi
fi

echo "[4/6] Instalando dependencias do projeto..."
if [ "$DB_MODE" = "sqlite" ]; then
  TMP_REQUIREMENTS="$(mktemp)"
  grep -Evi '^mysqlclient([<>=!~].*)?$' requirements.txt > "$TMP_REQUIREMENTS"
  pip install -r "$TMP_REQUIREMENTS"
  rm -f "$TMP_REQUIREMENTS"
else
  if ! pip install -r requirements.txt; then
    echo "ERRO: falha ao instalar dependencias MySQL (mysqlclient)." >&2
    echo "Instale as bibliotecas de sistema e execute novamente:" >&2
    echo "  Ubuntu/Debian: sudo apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config" >&2
    echo "  Fedora/RHEL:   sudo dnf install -y python3-devel mysql-devel gcc pkgconfig" >&2
    echo "  Arch:          sudo pacman -S --needed python mysql-clients mariadb-libs base-devel pkgconf" >&2
    exit 1
  fi
fi

echo "[5/6] Preparando arquivo .env..."
if [ ! -f "$ENV_FILE" ]; then
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "Arquivo .env criado a partir de .env.example."
fi

# Defaults seguros para desenvolvimento local.
sed -i "s/^DEBUG=.*/DEBUG=True/" "$ENV_FILE"
sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost:${PORT},http://127.0.0.1:${PORT}|" "$ENV_FILE"

if [ "$DB_MODE" = "sqlite" ]; then
  sed -i "s|^DB_ENGINE=.*|DB_ENGINE=django.db.backends.sqlite3|" "$ENV_FILE"
  sed -i "s|^DB_NAME=.*|DB_NAME=${ROOT_DIR}/db.sqlite3|" "$ENV_FILE"
  sed -i "s|^DB_USER=.*|DB_USER=|" "$ENV_FILE"
  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=|" "$ENV_FILE"
  sed -i "s|^DB_HOST=.*|DB_HOST=|" "$ENV_FILE"
  sed -i "s|^DB_PORT=.*|DB_PORT=|" "$ENV_FILE"
  echo "Banco selecionado: SQLite (db.sqlite3)."
else
  sed -i "s|^DB_ENGINE=.*|DB_ENGINE=django.db.backends.mysql|" "$ENV_FILE"
  sed -i "s|^DB_NAME=.*|DB_NAME=casa_inventory|" "$ENV_FILE"
  sed -i "s|^DB_HOST=.*|DB_HOST=localhost|" "$ENV_FILE"
  sed -i "s|^DB_PORT=.*|DB_PORT=3306|" "$ENV_FILE"
  echo "Banco selecionado: MySQL."
  echo "IMPORTANTE: ajuste DB_USER e DB_PASSWORD no .env se necessario."
fi

if [ "$DB_MODE" = "mysql" ]; then
  echo "[6/7] Garantindo base e utilizador MySQL..."

  DB_NAME="$(get_env_value DB_NAME)"
  DB_USER="$(get_env_value DB_USER)"
  DB_PASSWORD="$(get_env_value DB_PASSWORD)"
  DB_HOST="$(get_env_value DB_HOST)"
  DB_PORT="$(get_env_value DB_PORT)"
  DB_USER_HOST="${DB_USER_HOST:-localhost}"
  MYSQL_ADMIN_USER="${MYSQL_ADMIN_USER:-$DB_USER}"
  MYSQL_ADMIN_PASSWORD="${MYSQL_ADMIN_PASSWORD:-$DB_PASSWORD}"
  MYSQL_ADMIN_HOST="${MYSQL_ADMIN_HOST:-${DB_HOST:-localhost}}"
  MYSQL_ADMIN_PORT="${MYSQL_ADMIN_PORT:-${DB_PORT:-3306}}"

  if ! command -v mysql >/dev/null 2>&1; then
    echo "ERRO: cliente mysql nao encontrado, mas DB_MODE=mysql foi selecionado." >&2
    exit 1
  fi

  if [ -z "$DB_NAME" ]; then
    echo "ERRO: DB_NAME vazio no .env. Nao foi possivel criar a base." >&2
    exit 1
  fi

  if [ -z "$DB_USER" ]; then
    echo "ERRO: DB_USER vazio no .env. Defina um utilizador MySQL valido." >&2
    exit 1
  fi

  DB_NAME_ESCAPED="$(sql_ident_escape "$DB_NAME")"
  DB_USER_ESCAPED="$(sql_escape "$DB_USER")"
  DB_PASSWORD_ESCAPED="$(sql_escape "$DB_PASSWORD")"
  DB_USER_HOST_ESCAPED="$(sql_escape "$DB_USER_HOST")"

  MYSQL_SETUP_SQL=$(cat <<SQL
CREATE DATABASE IF NOT EXISTS \
\`$DB_NAME_ESCAPED\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER_ESCAPED'@'$DB_USER_HOST_ESCAPED' IDENTIFIED BY '$DB_PASSWORD_ESCAPED';
ALTER USER '$DB_USER_ESCAPED'@'$DB_USER_HOST_ESCAPED' IDENTIFIED BY '$DB_PASSWORD_ESCAPED';
GRANT ALL PRIVILEGES ON \`$DB_NAME_ESCAPED\`.* TO '$DB_USER_ESCAPED'@'$DB_USER_HOST_ESCAPED';
FLUSH PRIVILEGES;
SQL
)

  if ! run_mysql_admin_sql "$MYSQL_SETUP_SQL" "$MYSQL_ADMIN_USER" "$MYSQL_ADMIN_PASSWORD" "$MYSQL_ADMIN_HOST" "$MYSQL_ADMIN_PORT"; then
    echo "Falha com credenciais de admin padrao ($MYSQL_ADMIN_USER). Tentando root local via sudo..."
    if ! run_mysql_admin_sql "$MYSQL_SETUP_SQL" "root" "" "localhost" "3306"; then
      echo "ERRO: nao foi possivel criar base/utilizador MySQL." >&2
      echo "Defina MYSQL_ADMIN_USER e MYSQL_ADMIN_PASSWORD com um utilizador administrador valido." >&2
      exit 1
    fi
  fi

  echo "Base e utilizador MySQL configurados com sucesso: $DB_NAME / $DB_USER@$DB_USER_HOST"
  echo "[7/7] Validando configuracao e aplicando migrations..."
else
  echo "[6/6] Validando configuracao e aplicando migrations..."
fi

python manage.py check
python manage.py makemigrations inventory
python manage.py migrate inventory
python manage.py migrate

echo ""
echo "Projeto pronto. Iniciando servidor em http://${HOST}:${PORT}/"
exec python manage.py runserver "${HOST}:${PORT}"
