from http import HTTPStatus

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

    if election is None:
        return JsonResponse(status=HTTPStatus.NO_CONTENT)

    data = _afirmative_results_chart_data(election)

    return JsonResponse(data)


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
