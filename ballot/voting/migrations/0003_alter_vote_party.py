# Generated by Django 4.2.13 on 2024-05-13 00:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_election_vote_restult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='party',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='voting.politicalparty'),
        ),
    ]
