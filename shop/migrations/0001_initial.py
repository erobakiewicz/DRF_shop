# Generated by Django 4.2.4 on 2023-09-04 16:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('OP', 'OPEN'), ('CL', 'CLOSED')], default='OP', verbose_name='cart status')),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Carts',
            },
        ),
        migrations.CreateModel(
            name='GlobalProductLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit_size', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='global product limit size')),
            ],
            options={
                'verbose_name': 'Global product limit',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PD', 'PENDING'), ('CP', 'COMPLETED'), ('CL', 'CANCELLED')], default='PD', verbose_name='order status')),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=8, verbose_name='region name')),
                ('limit_size', models.IntegerField(verbose_name='region product limit size')),
                ('close_region', models.BooleanField(default=False, verbose_name='close region')),
                ('unlimited_access', models.BooleanField(default=False, verbose_name='unlimited')),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
        ),
        migrations.CreateModel(
            name='Shelf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='shelf name')),
            ],
            options={
                'verbose_name': 'Shelf',
                'verbose_name_plural': 'Shelves',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.shelf', verbose_name='shelf')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='shop.order')),
            ],
            options={
                'verbose_name': 'Order item',
                'verbose_name_plural': 'Order items',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.region'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='shop.cart')),
                ('shelf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.shelf', verbose_name='shelf name')),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Cart items',
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.region'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
