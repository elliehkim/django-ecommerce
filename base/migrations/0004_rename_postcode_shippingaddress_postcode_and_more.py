# Generated by Django 4.2.1 on 2023-06-18 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_product_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='postCode',
            new_name='postcode',
        ),
        migrations.RemoveField(
            model_name='order',
            name='paymentMethod',
        ),
        migrations.RemoveField(
            model_name='order',
            name='taxPrice',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='shippingPrice',
        ),
    ]