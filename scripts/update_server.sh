#!/usr/bin/env bash
set -euo pipefail

# Comando único de atualização do servidor: código, dependências, base de
# dados, estáticos e serviço web. Pode ser executado a partir de qualquer diretório.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/py_home}"
SERVICE_NAME="${SERVICE_NAME:-gunicorn}"
REMOTE_NAME="${REMOTE_NAME:-origin}"

cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERRO: $ROOT_DIR não é um repositório Git." >&2
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "ERRO: ambiente virtual não encontrado em $VENV_DIR." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "ERRO: existem alterações locais no servidor. Faça commit ou guarde-as antes de atualizar." >&2
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
GIT_BRANCH="${GIT_BRANCH:-$CURRENT_BRANCH}"
if [ -z "$GIT_BRANCH" ]; then
  echo "ERRO: não foi possível determinar a branch atual. Defina GIT_BRANCH." >&2
  exit 1
fi

echo "[1/7] A obter alterações de $REMOTE_NAME/$GIT_BRANCH..."
git fetch --prune "$REMOTE_NAME"
git pull --ff-only "$REMOTE_NAME" "$GIT_BRANCH"

echo "[2/7] A ativar ambiente virtual..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[3/7] A atualizar dependências..."
python -m pip install --requirement requirements.txt

echo "[4/7] A validar configuração Django..."
python manage.py check

echo "[5/7] A aplicar migrações..."
python manage.py migrate --noinput

echo "[6/7] A recolher ficheiros estáticos..."
python manage.py collectstatic --noinput

if [ -n "$SERVICE_NAME" ]; then
  echo "[7/7] A reiniciar $SERVICE_NAME..."
  sudo systemctl restart "$SERVICE_NAME"
  sudo systemctl is-active --quiet "$SERVICE_NAME"
  echo "Atualização concluída — serviço $SERVICE_NAME ativo."
else
  echo "[7/7] SERVICE_NAME vazio — serviço não reiniciado."
fi
