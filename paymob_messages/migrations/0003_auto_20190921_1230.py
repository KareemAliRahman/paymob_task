# Generated by Django 2.2.5 on 2019-09-21 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymob_messages', '0002_message_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='pub_date',
            field=models.DateTimeField(auto_now=True, verbose_name='date published'),
        ),
    ]
