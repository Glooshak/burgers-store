# Generated by Django 3.2.15 on 2022-11-20 08:01

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_productorder'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
                ('query_set_total_price', django.db.models.manager.Manager()),
            ],
        ),
    ]
