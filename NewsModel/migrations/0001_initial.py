# Generated by Django 2.1.1 on 2018-09-06 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='news',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.URLField()),
                ('url', models.URLField()),
                ('image_url', models.URLField()),
                ('title', models.CharField(max_length=50)),
                ('content', models.TextField()),
            ],
        ),
    ]
