# Generated by Django 3.0.5 on 2020-05-29 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0012_auto_20200528_2040'),
        ('students', '0009_auto_20200430_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='details',
            name='block_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institute.Blocks'),
        ),
        migrations.AlterField(
            model_name='details',
            name='floor',
            field=models.CharField(blank=True, choices=[('Ground', 'Ground'), ('First', 'First'), ('Second', 'Second')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='details',
            name='room_no',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
