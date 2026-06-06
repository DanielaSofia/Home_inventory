# AGENTS — Orientações para agentes de IA

![Check Migrations](https://github.com/DanielaSofia/Home_inventory/actions/workflows/check-migrations.yml/badge.svg?branch=master)

Este arquivo dá instruções concisas para agentes automatizados (Copilot, ChatOps, etc.) trabalharem neste repositório.

Objetivo rápido
# AGENTS — Orientações para agentes de IA

Este arquivo dá instruções concisas para agentes automatizados (Copilot, ChatOps, etc.) trabalharem neste repositório.

Objetivo rápido
- Projeto Django simples para inventário doméstico. Use `python manage.py` para tarefas comuns.

Comandos essenciais
- Instalar dependências: `pip install -r requirements.txt`
- Rodar servidor dev: `python manage.py runserver`
- Aplicar migrations: `python manage.py migrate`

Arquivos-chave (links)
- Projeto e configuração: [casa/settings.py](casa/settings.py)
- Entrypoint WSGI: [casa/wsgi.py](casa/wsgi.py)
- Script de gerenciamento: [manage.py](manage.py)
- App principal: [casa/inventory/](casa/inventory/)
- Requisitos: [requirements.txt](requirements.txt)
- Esquema inicial: [casa_struct.sql](casa_struct.sql)

Pontos importantes para agentes
- Não existem testes automatizados — evite executar pipelines de teste inexistentes.
- Configurações sensíveis (DB, SECRET_KEY) estão hardcoded em [casa/settings.py](casa/settings.py) — não as exponha em commits; prefira variáveis de ambiente.
- Migrations estão no diretório [casa/inventory/migrations/](casa/inventory/migrations/) — aplicar `migrate` quando alterar modelos.

Guia de contribuição rápida (para agentes)
- Para mudanças que afetam modelo de dados: atualize `models.py`, crie migration com `python manage.py makemigrations`, valide com `migrate`.
- Para alterações em assets estáticos: atualize [staticfiles/](staticfiles/) e execute coleta conforme o ambiente de implantação.

Sugestões de customizações úteis a criar
- Skill para rodar verificação rápida de DB/migrations.
- Prompt para revisar PRs que alterem `models.py` ou `migrations/`.

Skill disponível
- `skills/check_migrations_skill.md`: descreve um script automático para verificar se há mudanças de modelo sem migrations ([scripts/check_migrations.sh](scripts/check_migrations.sh)).

CI
- Existe um workflow do GitHub Actions em [.github/workflows/check-migrations.yml](.github/workflows/check-migrations.yml) que executa automaticamente o check de migrations em PRs que alterem `casa/inventory/`.

Contato
- Não existe documentação adicional no repositório; peça ao mantenedor esclarecimentos se necessário.
