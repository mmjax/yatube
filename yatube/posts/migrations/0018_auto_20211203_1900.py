# Generated by Django 2.2.16 on 2021-12-03 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20211202_2123'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
