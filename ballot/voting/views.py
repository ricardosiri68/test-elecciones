from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView

from voting.models import Voter, Vote, PoliticalParty, Election, VoteType
from voting.utils import make_vote


class VoteSuccessView(TemplateView):
    template_name = 'vote_success.html'


def results_view(request):
    """Render the main view for the election results."""
    election = _published_election()
    context = {'election': election}

    return render(request, 'index.html', context=context)


def results_json(request):
    """As a REST API this singleton endpoint provide the data for the rendering
    of elections result chart.
    """
    election = _published_election()

    if election is None:
        return JsonResponse(status=HTTPStatus.NO_CONTENT)

    data = _afirmative_results_chart_data(election)

    return JsonResponse(data)


def vote_view(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    party = None

    if voter.has_voted:
        return HttpResponseForbidden('You have already voted.')

    if request.method == 'POST':
        party_id = request.POST.get('party_id')
        vote_type = VoteType.BLANK if party_id == '' else VoteType.AFIRMATIVE

        if vote_type is VoteType.AFIRMATIVE:
            party = PoliticalParty.objects.get(id=party_id) if party_id else None

        vote = Vote.objects.create(
            vote_type=vote_type, election=Election.objects.filter(is_open=True).first(), party=party
        )

        make_vote(voter, vote)
        return redirect('vote_success')

    political_parties = PoliticalParty.objects.all()

    return render(
        request,
        'vote_form.html',
        {
            'voter': voter,
            'political_parties': political_parties,
            'vote_types': VoteType.choices,
        },
    )


def _published_election():
    return Election.objects.filter(published=True).order_by('-date').first()


def _afirmative_results_chart_data(election: Election) -> dict:
    afirmative_results = election.results.filter(vote_type=VoteType.AFIRMATIVE).all()

    labels = []
    percentages = []

    for result in afirmative_results:
        labels.append(result.party.party_name)
        percentages.append(result.percentage)

    return {
        'labels': labels,
        'datasets': [
            {
                'label': 'Elecciones 2023',
                'data': percentages,
                'backgroundColor': ['rgb(255, 100, 100)', 'rgb(54, 162, 235)'],
                'hoverOffset': 4,
            }
        ],
    }
