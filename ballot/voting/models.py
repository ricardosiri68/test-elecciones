from django.utils.translation import gettext_lazy as _
from django.db import models


class Voter(models.Model):

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dni = models.PositiveIntegerField(unique=True)
    birth_date = models.DateField()
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:

        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'


class PoliticalParty(models.Model):

    party_number = models.PositiveIntegerField(unique=True)
    party_name = models.CharField(max_length=50)
    president = models.CharField(max_length=100)
    vice_president = models.CharField(max_length=100)
    slogan = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.party_number} - {self.party_name}'

    class Meta:

        verbose_name = 'Political Party'
        verbose_name_plural = 'Political Parties'


class Election(models.Model):

    is_open = models.BooleanField(default=True)
    published = models.BooleanField(default=True)
    date = models.DateField()


class VoteType(models.TextChoices):

    AFIRMATIVE = 'A', _('Afirmative')
    BLANK = 'B', _('Blank')
    NULL = 'N', _('Null')


class Result(models.Model):

    vote_type = models.CharField(max_length=1, choices=VoteType.choices, default=VoteType.NULL)
    election = models.ForeignKey('Election', on_delete=models.PROTECT, related_name='results')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    votes = models.IntegerField()
    party = models.ForeignKey('PoliticalParty', on_delete=models.PROTECT, null=True, blank=True)


class Vote(models.Model):

    vote_type = models.CharField(max_length=1, choices=VoteType.choices, default=VoteType.NULL)
    election = models.ForeignKey('Election', on_delete=models.PROTECT)
    party = models.ForeignKey('PoliticalParty', on_delete=models.PROTECT, null=True)
