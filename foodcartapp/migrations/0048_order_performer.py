# Generated by Django 3.2.15 on 2022-11-23 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_order_pay_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='Ресторан(ы)'),
        ),
    ]