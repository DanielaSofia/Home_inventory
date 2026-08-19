#!/usr/bin/env bash
set -euo pipefail

echo "Verificando ambiente e migrations..."

if [ -f py_home/bin/activate ]; then
  echo "Ativando virtualenv py_home"
  # shellcheck source=/dev/null
  source py_home/bin/activate
fi

echo "Executando: python manage.py makemigrations --dry-run --check"
if ! python manage.py makemigrations --dry-run --check; then
  echo "ERRO: existem mudanças de modelos sem migrations. Rode: python manage.py makemigrations" 1>&2
  exit 2
fi

echo "Mostrando plano de migrations (se houver):"
python manage.py migrate --plan || true

echo "OK: verificação de migrations concluída sem problemas." 
