from django.db import migrations, models


def migrar_compras_pendentes(apps, schema_editor):
    Consumivel = apps.get_model("inventory", "Consumivel")
    Consumivel.objects.filter(comprado=False).update(na_lista_compras=True)


class Migration(migrations.Migration):
    dependencies = [("inventory", "0010_add_default_divisoes")]

    operations = [
        migrations.AddField(
            model_name="consumivel",
            name="na_lista_compras",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(migrar_compras_pendentes, migrations.RunPython.noop),
    ]
