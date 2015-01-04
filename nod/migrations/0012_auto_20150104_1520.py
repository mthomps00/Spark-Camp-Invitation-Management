# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nod', '0011_auto_20150104_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votinground',
            name='num_votes',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
