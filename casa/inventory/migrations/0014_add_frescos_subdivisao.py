from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventory", "0013_add_temperos_subdivisao")]

    operations = [
        migrations.AlterField(
            model_name="consumivel",
            name="subdivisao",
            field=models.CharField(
                choices=[
                    ("congelados", "Congelados"),
                    ("fatiados", "Fatiados"),
                    ("conservas", "Conservas"),
                    ("frutas_legumes", "Frutas e legumes"),
                    ("temperos", "Temperos"),
                    ("frescos", "Frescos"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=30,
            ),
        ),
    ]