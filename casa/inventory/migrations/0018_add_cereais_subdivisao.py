from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0017_add_molhos_doces_subdivisao")]

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
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]