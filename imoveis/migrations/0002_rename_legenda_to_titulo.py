from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imovelfoto',
            old_name='legenda',
            new_name='titulo',
        ),
        migrations.AlterField(
            model_name='imovelfoto',
            name='titulo',
            field=models.CharField(
                blank=True,
                help_text='Nome do cômodo mostrado embaixo da foto, ex: Sala, Quarto 1, Varanda.',
                max_length=120,
                verbose_name='título',
            ),
        ),
    ]
