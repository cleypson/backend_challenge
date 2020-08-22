# Generated by Django 3.1 on 2020-08-22 02:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gas_capacity', models.FloatField(default=45, verbose_name='Gas Capacity in Liter')),
                ('current_gas', models.FloatField(default=0.0, verbose_name='Current Gas in %')),
                ('max_quantity_tyres', models.IntegerField(default=4, verbose_name='Quantity of Tires')),
                ('km_per_liter', models.FloatField(default=8, verbose_name='Gas consumption per liter')),
                ('odometer', models.FloatField(default=0.0, verbose_name='Odometer')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Car',
                'verbose_name_plural': 'Cars',
            },
        ),
        migrations.CreateModel(
            name='Tyre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degradation', models.FloatField(default=0, verbose_name='Degradation in %')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'In Use'), (2, 'Available'), (3, 'Discarded'), (4, 'Shatter')], default=2, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.car', verbose_name='Car')),
            ],
            options={
                'verbose_name': 'Tyre',
                'verbose_name_plural': 'Tyres',
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(verbose_name='Distance in KM')),
                ('travelled_distance', models.FloatField(null=True, verbose_name='Travelled distance in KM')),
                ('description', models.TextField(verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.car', verbose_name='Car')),
            ],
            options={
                'verbose_name': 'Trip',
                'verbose_name_plural': 'Trips',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(null=True, verbose_name='Distance in KM')),
                ('fueled', models.FloatField(default=0.0, verbose_name='Fueled in liter(s)')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Refuelling'), (2, 'Change tyre'), (3, 'New tyre')], default=2, verbose_name='Order Type')),
                ('description', models.TextField(verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.car', verbose_name='Car')),
                ('tyre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tyre', verbose_name='Tyre')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
        ),
    ]
