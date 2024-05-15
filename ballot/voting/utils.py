from voting.exceptions import AlreadyVotedError, PublishOpenElectionError
from voting.models import Election, PoliticalParty, Result, Vote, VoteType, Voter


def has_voted(dni):
    """With a given dni check if the voter has already voted."""
    try:
        voter = Voter.objects.get(dni=dni)
        return voter.has_voted
    except Voter.DoesNotExist:
        return None


def has_voted_percentage():
    """Return the voted percentage."""
    total_voters = Voter.objects.count()
    voted_voters = Voter.objects.filter(has_voted=True).count()

    if total_voters == 0:
        return 0

    return make_percentage(total_voters, voted_voters)


def make_vote(voter: Voter, vote: Vote):
    """Check the conditions of the voter and add a new vote if there match."""
    if has_voted(voter.dni) is True:
        raise AlreadyVotedError(f'The voter {voter.dni}, already has voted')

    voter.has_voted = True
    Vote.save(vote)
    Voter.save(voter)


def close_election(election: Election):
    """Generate the results of the election and change it to closed state."""
    make_results(election)
    election.is_open = False
    election.save()


def publish_results(election: Election):
    """Change the state of the election to published if it's closed."""
    if election.is_open:
        raise PublishOpenElectionError('You need close the election to publish the results.')

    election.published = True
    election.save()


def make_results(election: Election):
    """Generate the result of the elections."""
    total = Vote.objects.count()
    total_afirmative = Vote.objects.filter(election=election, vote_type=VoteType.AFIRMATIVE).count()

    make_non_affirmative_result(election, VoteType.BLANK, total)
    make_non_affirmative_result(election, VoteType.NULL, total)

    for party in PoliticalParty.objects.all():
        make_affirmative_result(election, party, total_afirmative)


def make_non_affirmative_result(election: Election, vote_type: VoteType, total: int):
    """Generate the non afirmative result objects only."""
    non_afirmative_count = Vote.objects.filter(election=election, vote_type=vote_type).count()

    Result.objects.create(
        vote_type=vote_type,
        election=election,
        percentage=make_percentage(total, non_afirmative_count),
        votes=non_afirmative_count,
    )


def make_affirmative_result(election: Election, party: PoliticalParty, total: int):
    """Generate the affirmative resule objects only."""
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
    """Calculate a percentange."""
    return (current / total) * 100
