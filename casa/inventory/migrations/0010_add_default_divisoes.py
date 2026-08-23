from django.db import migrations


DIVISOES_PADRAO = (
    "WC",
    "Cozinha",
    "Escritório",
    "Quarto",
    "Sala de estar",
    "Marquise",
    "Varanda",
)


def adicionar_divisoes_padrao(apps, schema_editor):
    """Cria as divisões iniciais sem repetir nomes já registados."""

    Divisao = apps.get_model("inventory", "Divisao")
    nomes_existentes = {
        nome.casefold() for nome in Divisao.objects.values_list("nome", flat=True)
    }
    Divisao.objects.bulk_create(
        [Divisao(nome=nome) for nome in DIVISOES_PADRAO if nome.casefold() not in nomes_existentes]
    )


class Migration(migrations.Migration):
    dependencies = [("inventory", "0009_remove_historicocompra_consumivel_and_more")]

    operations = [migrations.RunPython(adicionar_divisoes_padrao, migrations.RunPython.noop)]
