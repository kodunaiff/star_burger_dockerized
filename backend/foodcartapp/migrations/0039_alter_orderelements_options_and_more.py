# Generated by Django 4.2 on 2024-03-02 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderelements'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderelements',
            options={'ordering': ['order']},
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_number',
        ),
    ]
