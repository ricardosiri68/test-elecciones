from factory import django, Faker

from voting.models import Voter, Election, PoliticalParty


class VoterFactory(django.DjangoModelFactory):
    class Meta:
        model = Voter

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    dni = Faker('random_int', min=0, max=57000000)
    birth_date = Faker('date_of_birth')
    has_voted = False


class ElectionFactory(django.DjangoModelFactory):
    class Meta:
        model = Election

    date = Faker('date')


def make_parties():
    paries = (
        PoliticalParty(
            party_number=1,
            party_name='A party',
            president='Val',
            vice_president='Rick',
            slogan='we have why',
        ),
        PoliticalParty(
            party_number=2,
            party_name='other party',
            president='Jhon',
            vice_president='Kelly',
            slogan='long life and properity',
        ),
    )
    PoliticalParty.objects.bulk_create(paries)

    return paries
