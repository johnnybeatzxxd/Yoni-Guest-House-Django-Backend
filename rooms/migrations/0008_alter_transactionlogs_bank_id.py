# Generated by Django 5.1.3 on 2024-11-15 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0007_alter_transactionlogs_account_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionlogs',
            name='bank_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]