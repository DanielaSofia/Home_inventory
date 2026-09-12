from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0011_consumivel_na_lista_compras")]

    operations = [
        migrations.AddField(
            model_name="consumivel",
            name="subdivisao",
            field=models.CharField(
                choices=[
                    ("congelados", "Congelados"),
                    ("fatiados", "Fatiados"),
                    ("conservas", "Conservas"),
                    ("frutas_legumes", "Frutas e legumes"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]