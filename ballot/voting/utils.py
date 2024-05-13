from .models import Voter, Vote, VoteType, Election, Result, PoliticalParty
from .exceptions import AlreadyVotedError, PublishOpenElectionError


def has_voted(dni):
    try:
        voter = Voter.objects.get(dni=dni)
        return voter.has_voted
    except Voter.DoesNotExist:
        return None


def has_voted_percentage():
    total_voters = Voter.objects.count()
    voted_voters = Voter.objects.filter(has_voted=True).count()

    if total_voters == 0:
        return 0

    return (voted_voters / total_voters) * 100


def make_vote(voter: Voter, vote: Vote):

    if has_voted(voter.dni) is True:
        raise AlreadyVotedError(f'The voter {voter.dni}, already has voted')

    voter.has_voted = True
    Vote.save(vote)
    Voter.save(voter)


def close_election(election: Election):

    election.is_open = False
    make_results(election)
    election.save()


def publish_results(election: Election):

    if election.is_open:
        raise PublishOpenElectionError('You need close the election to publish the results.')

    election.published = True
    election.save()


def make_results(election: Election):

    total = Vote.objects.count()
    total_afirmative = Vote.objects.filter(election=election, vote_type=VoteType.AFIRMATIVE).count()

    make_non_afirmative_result(election, VoteType.BLANK, total)
    make_non_afirmative_result(election, VoteType.NULL, total)

    for party in PoliticalParty.objects.all():
        make_afirmative_result(election, party, total_afirmative)


def make_non_afirmative_result(election: Election, vote_type: VoteType, total: int):
    non_afirmative_count = Vote.objects.filter(election=election, vote_type=vote_type).count()

    Result.objects.create(
        vote_type=vote_type,
        election=election,
        percentage=make_percentage(total, non_afirmative_count),
        votes=non_afirmative_count,
    )


def make_afirmative_result(election: Election, party: PoliticalParty, total: int):
    party_votes = Vote.objects.filter(
        election=election, vote_type=VoteType.AFIRMATIVE, party=party
    ).count()
    Result.objects.create(
        vote_type=VoteType.AFIRMATIVE,
        election=election,
        percentage=make_percentage(total, party_votes),
        votes=party_votes,
        party=party,
    )


def make_percentage(total, current):
    return (current / total) * 100
