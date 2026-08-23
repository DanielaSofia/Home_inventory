#!/usr/bin/env bash
set -euo pipefail

# Atualiza o servidor (Raspberry Pi) a partir do git: pull, dependências,
# migrações, ficheiros estáticos e reinício opcional do serviço.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/py_home"
GIT_BRANCH="${GIT_BRANCH:-master}"
SERVICE_NAME="${SERVICE_NAME:-gunicorn}"

cd "$ROOT_DIR"

echo "[1/5] git pull (branch: $GIT_BRANCH)..."
git fetch origin "$GIT_BRANCH"
git checkout "$GIT_BRANCH"
git pull origin "$GIT_BRANCH"

if [ -f "$VENV_DIR/bin/activate" ]; then
  echo "[2/5] Ativando virtualenv em $VENV_DIR..."
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
else
  echo "ERRO: virtualenv não encontrado em $VENV_DIR. Corre primeiro scripts/setup_and_run.sh." >&2
  exit 1
fi

echo "[3/5] Instalando dependências..."
pip install -r requirements.txt

echo "[4/5] Aplicando migrações..."
python manage.py migrate

echo "[5/5] Recolhendo ficheiros estáticos..."
python manage.py collectstatic --noinput

if [ -n "$SERVICE_NAME" ]; then
  echo "Reiniciando serviço $SERVICE_NAME (gunicorn)..."
  sudo systemctl restart "$SERVICE_NAME"
  sudo systemctl status "$SERVICE_NAME" --no-pager
else
  echo "SERVICE_NAME vazio — reinicia manualmente o gunicorn para aplicar as alterações."
fi

echo "Deploy concluído."
