# Generated by Django 2.2.12 on 2021-09-18 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refund',
            name='payment_id',
            field=models.CharField(default='v', max_length=200),
        ),
    ]