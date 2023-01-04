# Generated by Django 4.1.5 on 2023-01-04 11:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_alter_inventory_created_by_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to=settings.AUTH_USER_MODEL)),
                ('shop', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_shop', to='app.shop')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255, null=True)),
                ('item_code', models.CharField(max_length=20, null=True)),
                ('quantity', models.PositiveIntegerField()),
                ('amount', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_items', to='app.invoice')),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inventory_invoices', to='app.inventory')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]