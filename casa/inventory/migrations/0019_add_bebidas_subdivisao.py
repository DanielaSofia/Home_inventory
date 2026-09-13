from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0018_add_cereais_subdivisao")]

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
                    ("temperos", "Temperos"),
                    ("frescos", "Frescos"),
                    ("molhos", "Molhos"),
                    ("doces", "Doces"),
                    ("cereais", "Cereais"),
                    ("bebidas", "Bebidas"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]