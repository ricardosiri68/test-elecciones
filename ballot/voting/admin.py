from django.contrib import admin

from .models import Voter, PoliticalParty, Election, Result


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'dni', 'birth_date', 'has_voted')
    search_fields = ('first_name', 'last_name', 'dni')
    list_filter = ('has_voted',)


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_number', 'party_name', 'president', 'vice_president', 'slogan')
    search_fields = ('party_number', 'party_name')


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_open', 'published')
    search_fields = ('date', 'is_open')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('election', 'vote_type', 'party', 'percentage', 'votes')
    search_fields = ('vote_type',)
