# Generated by Django 5.0.6 on 2024-05-26 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_rename_timework_worker_timework_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='positionlist',
            old_name='salary',
            new_name='salaryOfTime',
        ),
        migrations.AlterField(
            model_name='buildobject',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
