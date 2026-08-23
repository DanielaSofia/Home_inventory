#!/usr/bin/env bash
set -euo pipefail

# Comando único de atualização do servidor: código, dependências, base de
# dados, estáticos e serviço web. Pode ser executado a partir de qualquer diretório.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/py_home}"
SERVICE_NAME="${SERVICE_NAME:-gunicorn}"
REMOTE_NAME="${REMOTE_NAME:-origin}"
SKIP_GIT_UPDATE="${SKIP_GIT_UPDATE:-}"

cd "$ROOT_DIR"

if [ -z "$SKIP_GIT_UPDATE" ] && [ -t 0 ]; then
  read -r -p "Ignorar atualização Git e usar as alterações locais do servidor? [S/n] " choice
  case "$choice" in
    [nN]) SKIP_GIT_UPDATE=false ;;
    *) SKIP_GIT_UPDATE=true ;;
  esac
fi

SKIP_GIT_UPDATE="${SKIP_GIT_UPDATE:-true}"
case "$SKIP_GIT_UPDATE" in
  true|TRUE|1|yes|YES) SKIP_GIT_UPDATE=true ;;
  false|FALSE|0|no|NO) SKIP_GIT_UPDATE=false ;;
  *)
    echo "ERRO: SKIP_GIT_UPDATE deve ser true ou false." >&2
    exit 1
    ;;
esac

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "ERRO: ambiente virtual não encontrado em $VENV_DIR." >&2
  exit 1
fi

if [ "$SKIP_GIT_UPDATE" = true ]; then
  echo "[1/8] A ignorar Git: serão usadas as alterações locais do servidor."
else
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERRO: $ROOT_DIR não é um repositório Git." >&2
    exit 1
  fi

  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERRO: existem alterações locais no servidor. Faça commit, guarde-as ou use SKIP_GIT_UPDATE=true." >&2
    exit 1
  fi

  CURRENT_BRANCH="$(git branch --show-current)"
  GIT_BRANCH="${GIT_BRANCH:-$CURRENT_BRANCH}"
  if [ -z "$GIT_BRANCH" ]; then
    echo "ERRO: não foi possível determinar a branch atual. Defina GIT_BRANCH." >&2
    exit 1
  fi

  echo "[1/8] A obter alterações de $REMOTE_NAME/$GIT_BRANCH..."
  git fetch --prune "$REMOTE_NAME"
  git pull --ff-only "$REMOTE_NAME" "$GIT_BRANCH"
fi

echo "[2/8] A ativar ambiente virtual..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[3/8] A atualizar dependências..."
python -m pip install --requirement requirements.txt

echo "[4/8] A validar configuração Django..."
python manage.py check

echo "[5/8] A criar migrações pendentes..."
python manage.py makemigrations inventory --noinput

echo "[6/8] A aplicar migrações..."
python manage.py migrate --noinput

echo "[7/8] A recolher ficheiros estáticos..."
python manage.py collectstatic --noinput

if [ -n "$SERVICE_NAME" ]; then
  echo "[8/8] A reiniciar $SERVICE_NAME..."
  sudo systemctl restart "$SERVICE_NAME"
  sudo systemctl is-active --quiet "$SERVICE_NAME"
  echo "Atualização concluída — serviço $SERVICE_NAME ativo."
else
  echo "[8/8] SERVICE_NAME vazio — serviço não reiniciado."
fi
