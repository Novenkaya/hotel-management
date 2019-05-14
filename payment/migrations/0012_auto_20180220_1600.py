# Generated by Django 2.0 on 2018-02-20 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_checkout_stay_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='pay_amount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='checkout',
            name='total_amount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
