# Generated by Django 2.2.13 on 2020-10-16 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='org_name',
            field=models.CharField(blank=True, max_length=255, verbose_name="User's Organization"),
        ),
    ]