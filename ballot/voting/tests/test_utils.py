from decimal import Decimal
import pytest

from voting.exceptions import AlreadyVotedError, PublishOpenElectionError
from voting.models import VoteType, Vote
from voting.tests.factories import VoterFactory, ElectionFactory, make_parties
from voting.utils import close_election, has_voted, has_voted_percentage, make_vote, publish_results


# has_voted tests
@pytest.mark.django_db
@pytest.mark.parametrize(
    'has_voted_value, expected_result',
    [
        (True, True),  # Test case for has_voted=True
        (False, False),  # Test case for has_voted=False
    ],
)
def test_has_voted(has_voted_value, expected_result):
    voter = VoterFactory(has_voted=has_voted_value)

    assert has_voted(voter.dni) == expected_result


@pytest.mark.django_db
def test_has_voted_not_exits():
    assert has_voted(1234) is None


# has_voted_percentage tests
@pytest.mark.django_db
@pytest.mark.parametrize(
    'voters_data, expected_percentage',
    [
        ([], 0),  # Test case for 0 voters
        ([(True, 1), (True, 2), (True, 3), (True, 4)], 100),  # Test case for all voters voted
        ([(True, 1), (True, 2), (False, 3), (False, 4)], 50),  # Test case for 50-50
    ],
)
def test_has_voted_percentage(voters_data, expected_percentage):
    for voted, dni in voters_data:
        VoterFactory(has_voted=voted, dni=dni)

    voted_percentage = has_voted_percentage()

    assert voted_percentage == pytest.approx(expected_percentage, abs=0.01)


@pytest.mark.django_db
def test_make_vote_afirmative():

    election = ElectionFactory()
    voter = VoterFactory()
    party, _ = make_parties()

    make_vote(voter, Vote(election=election, party=party, vote_type=VoteType.AFIRMATIVE))

    assert voter.has_voted


@pytest.mark.django_db
def test_make_vote_blank():
    election = ElectionFactory()
    voter = VoterFactory()
    party, _ = make_parties()

    make_vote(voter, Vote(election=election, party=None, vote_type=VoteType.BLANK))

    assert voter.has_voted


@pytest.mark.django_db
def test_make_same_vote_twice_fails():
    election = ElectionFactory()
    voter = VoterFactory()
    party, _ = make_parties()

    make_vote(voter, Vote(election=election, vote_type=VoteType.BLANK))

    assert voter.has_voted

    with pytest.raises(AlreadyVotedError):
        make_vote(voter, Vote(election=election, party=None, vote_type=VoteType.BLANK))


@pytest.mark.django_db
def test_close_election():
    election = ElectionFactory()
    oficialism, opposition = make_parties()

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=oficialism)
    )

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=opposition)
    )

    close_election(election)

    assert not election.is_open


@pytest.mark.django_db
def test_results_of_closed_election():
    election = ElectionFactory()
    oficialism, opposition = make_parties()
    expected_results = {
        VoteType.BLANK: 25,
        oficialism.party_name: Decimal('66.67'),
        opposition.party_name: Decimal('33.33'),
    }

    make_vote(VoterFactory(), Vote(election=election, vote_type=VoteType.BLANK))

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=oficialism)
    )

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=oficialism)
    )

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=opposition)
    )

    close_election(election)
    results = {
        VoteType.BLANK: election.results.filter(vote_type=VoteType.BLANK).first().percentage,
        oficialism.party_name: election.results.filter(
            party=oficialism, vote_type=VoteType.AFIRMATIVE
        )
        .first()
        .percentage,
        opposition.party_name: election.results.filter(
            party=opposition, vote_type=VoteType.AFIRMATIVE
        )
        .first()
        .percentage,
    }

    assert results == expected_results


@pytest.mark.django_db
def test_make_election_result_public():
    election = ElectionFactory()
    oficialism, opposition = make_parties()

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=oficialism)
    )

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=opposition)
    )

    close_election(election)
    publish_results(election)

    assert election.published


@pytest.mark.django_db
def test_make_open_election_result_public_fails():
    election = ElectionFactory()
    oficialism, opposition = make_parties()

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=oficialism)
    )

    make_vote(
        VoterFactory(), Vote(election=election, vote_type=VoteType.AFIRMATIVE, party=opposition)
    )

    with pytest.raises(PublishOpenElectionError):
        publish_results(election)
