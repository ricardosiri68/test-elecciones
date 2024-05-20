from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from voting.models import Voter, PoliticalParty, Election, Result, Vote
from voting.utils import close_election


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'dni', 'birth_date', 'has_voted', 'voting_link')
    search_fields = ('dni',)  # Búsqueda por DNI

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:voter_id>/generate_link/',
                self.admin_site.admin_view(self.generate_link),
                name='generate_link',
            ),
        ]
        return custom_urls + urls

    def generate_link(self, request, voter_id):
        voter = Voter.objects.get(id=voter_id)
        if voter and not voter.has_voted:
            unique_link = request.build_absolute_uri(reverse('vote', args=[voter.id]))
            self.message_user(
                request,
                format_html('Enlace generado: <a href="{}">{}</a>', unique_link, unique_link),
            )
        else:
            self.message_user(request, 'El votante no existe o ya ha votado', level='error')
        return HttpResponseRedirect(f'../{voter_id}/change/')

    def voting_link(self, obj):
        if not obj.has_voted:
            return format_html(
                '<a class="button" href="{}">Generar enlace de votación</a>',
                reverse('admin:generate_link', args=[obj.id]),
            )
        return 'Ya ha votado'

    voting_link.short_description = 'Enlace de votación'

    def render_change_form(self, request, context, *args, **kwargs):
        voter = kwargs.get('obj')
        extra = context.get('extra', {})
        if voter and not voter.has_voted:
            extra['generate_link'] = format_html(
                '<a class="button" href="{}">Generar enlace de votación</a>',
                f'../{voter.id}/generate_link/',
            )
        context.update(extra)
        return super().render_change_form(request, context, *args, **kwargs)


@admin.register(PoliticalParty)
class PoliticalPartyAdmin(admin.ModelAdmin):
    list_display = ('party_number', 'party_name', 'president', 'vice_president', 'slogan')
    search_fields = ('party_number', 'party_name')


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_open', 'published', 'close_election_link')
    search_fields = ('date', 'is_open')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:election_id>/close_election/',
                self.admin_site.admin_view(self.close_election),
                name='close_election',
            ),
        ]
        return custom_urls + urls

    def close_election_link(self, election):
        close_message = '¿Estás seguro de que deseas finalizar esta elección?'
        if election.is_open:
            return format_html(
                '<a class="button" onclick="confirm(\'{}\')" href="{}">Cerrar elección</a>',
                close_message,
                reverse('admin:close_election', args=[election.id]),
            )

        return 'Ya esta cerrada'

    def close_election(self, request, election_id):
        election = Election.objects.get(id=election_id)

        if election and election.is_open:
            close_election(election)
            self.message_user(
                request,
                format_html('La eleccion se ha cerrqado'),
            )
        else:
            self.message_user(request, 'La eleccion ya se encuentra cerrada', level='error')

        return HttpResponseRedirect('/admin/voting/election')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('election', 'vote_type', 'party', 'percentage', 'votes')
    search_fields = ('vote_type',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = 'election', 'vote_type', 'party'
