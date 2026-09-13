from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0014_add_frescos_subdivisao")]

    operations = [
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
                    ("frutas_legumes", "Frutas e legumes (anteriores)"),
                    ("temperos", "Temperos"),
                    ("frescos", "Frescos"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]