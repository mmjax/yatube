# Generated by Django 2.2.16 on 2021-12-01 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20211201_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='posts.Post', verbose_name='Пост'),
        ),
    ]