# Generated by Django 4.0 on 2021-12-22 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('qty_change', models.IntegerField()),
                ('activity', models.CharField(choices=[('C', 'Create'), ('U', 'Update'), ('M', 'Move')], max_length=1)),
                ('notes', models.CharField(blank=True, max_length=150, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='users.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
    ]
