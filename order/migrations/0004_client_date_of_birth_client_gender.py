# Generated by Django 5.1.5 on 2025-03-13 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_orderitems_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='date_of_birth',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='gender',
            field=models.CharField(default='', max_length=1),
        ),
    ]
