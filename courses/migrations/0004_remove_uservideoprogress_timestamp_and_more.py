# Generated by Django 4.2.9 on 2024-04-28 09:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_uservideoprogress"),
    ]

    operations = [
        migrations.RemoveField(model_name="uservideoprogress", name="timestamp",),
        migrations.AddField(
            model_name="uservideoprogress",
            name="relative_timestamp",
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
