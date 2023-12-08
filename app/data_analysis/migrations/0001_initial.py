# Generated by Django 4.2.7 on 2023-11-21 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('store_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('name', models.TextField()),
                ('code', models.TextField()),
                ('category', models.TextField()),
                ('category_code', models.TextField()),
                ('price', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'product',
                'managed': False,
            },
        ),
    ]
