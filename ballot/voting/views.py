from django.http import JsonResponse
from django.shortcuts import render

from voting.models import Election, VoteType


def index(request):
    """Render the main view for the election results."""
    election = _published_election()
    context = {'election': election}

    return render(request, 'index.html', context=context)


def results_json(request):
    """As a REST API this singleton endpoint provide the data for the rendering
    of elections result chart.
    """
    election = _published_election()
    afirmative_results = election.results.filter(vote_type=VoteType.AFIRMATIVE).all()
    data = {
        'labels': [result.party.party_name for result in afirmative_results],
        'datasets': [
            {
                'label': 'Elecciones 2023',
                'data': [result.percentage for result in afirmative_results],
                'backgroundColor': ['rgb(255, 100, 100)', 'rgb(54, 162, 235)'],
                'hoverOffset': 4,
            }
        ],
    }

    return JsonResponse(data)


def _published_election():
    return Election.objects.filter(published=True).order_by('-date').first()
