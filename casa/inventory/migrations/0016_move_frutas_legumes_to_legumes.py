from django.db import migrations, models


def mover_frutas_legumes_para_legumes(apps, schema_editor):
    del schema_editor
    Consumivel = apps.get_model("inventory", "Consumivel")
    Consumivel.objects.filter(subdivisao="frutas_legumes").update(subdivisao="legumes")


class Migration(migrations.Migration):
    dependencies = [("inventory", "0015_separate_frutas_legumes")]

    operations = [
        migrations.RunPython(mover_frutas_legumes_para_legumes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="consumivel",
            name="subdivisao",
            field=models.CharField(
                choices=[
                    ("congelados", "Congelados"),
                    ("fatiados", "Fatiados"),
                    ("conservas", "Conservas"),
                    ("frutas", "Frutas"),
                    ("legumes", "Legumes"),
                    ("temperos", "Temperos"),
                    ("frescos", "Frescos"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]