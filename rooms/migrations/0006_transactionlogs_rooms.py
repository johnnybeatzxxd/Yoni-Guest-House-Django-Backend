# Generated by Django 5.1.3 on 2024-11-15 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_transactionlogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionlogs',
            name='rooms',
            field=models.ManyToManyField(related_name='transaction_logs', to='rooms.rooms'),
        ),
    ]