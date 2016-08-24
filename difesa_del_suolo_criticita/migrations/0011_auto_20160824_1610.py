# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-24 14:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('difesa_del_suolo_criticita', '0010_auto_20160824_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentazionecollegata',
            name='relate',
            field=models.ForeignKey(db_column='segn_fk', null=True, on_delete=django.db.models.deletion.CASCADE, to='difesa_del_suolo_criticita.Segnalazione', to_field='codice_segnalazione'),
        ),
        migrations.AlterField(
            model_name='segnalazione',
            name='codice_segnalazione',
            field=models.CharField(db_column='codsegn', max_length=20, unique=True),
        ),
    ]
