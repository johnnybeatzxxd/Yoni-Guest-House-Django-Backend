# Generated by Django 5.1.3 on 2024-11-15 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0008_alter_transactionlogs_bank_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionlogs',
            name='chapa_reference',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
