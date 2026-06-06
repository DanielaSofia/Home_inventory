# Skill: Verificação automática de migrations

Resumo
- Skill simples para verificar se alterações nos modelos requerem migrations novas e para mostrar o plano de migrations pendentes.

Quando executar
- Em PRs que modificam `casa/inventory/models.py` ou qualquer arquivo em `casa/inventory/migrations/`.
- Como verificação local antes de abrir PR.

O que faz
- Executa o script [scripts/check_migrations.sh](scripts/check_migrations.sh) que:
  - ativa a virtualenv `py_home` se presente;
  - executa `python manage.py makemigrations --dry-run --check` (falhará se houver mudanças sem migration);
  - executa `python manage.py migrate --plan` para mostrar o plano de migrations.

Como usar (manual)
1. Ative seu ambiente virtual (opcional): `source py_home/bin/activate`.
2. Rode o script: `bash scripts/check_migrations.sh`.

Saídas e códigos de saída
- Código `0`: tudo ok.
- Código `2`: existem mudanças de modelo sem migrations (action: rodar `python manage.py makemigrations`).

Recomendações para agentes automatizados
- Rodar este skill automaticamente ao detectar mudanças em `models.py` numa PR.
- Em pipelines CI: adicionar um job que execute `bash scripts/check_migrations.sh` e falhe em caso de código 2.
- Não tente aplicar migrations automaticamente em CI sem aprovação humana.

Links úteis
- Projeto principal: [casa/settings.py](casa/settings.py)
