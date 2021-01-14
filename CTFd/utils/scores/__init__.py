from sqlalchemy.sql.expression import union_all

from CTFd.cache import cache
from CTFd.models import Challenges, Solves, Users, db, BadgesEntries
from CTFd.utils import get_config
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils.modes import get_model

# TODO ISEN : remove this file or rewrite all the code (because Score is not suppose to exist at the end of the project)

@cache.memoize(timeout=60)
def get_standings(count=None, admin=False, fields=[], badges_entries=None):
    """
    Get standings as a list of tuples containing account_id, name, and score e.g. [(account_id, team_name, score)].

    Ties are broken by who reached a given score first based on the solve ID. Two users can have the same score but one
    user will have a solve ID that is before the others. That user will be considered the tie-winner.

    Challenges & Awards with a value of zero are filtered out of the calculations to avoid incorrect tie breaks.
    """
    Model = get_model()

    #scores = (
        #db.session.query(
         #   Solves.account_id.label("account_id"),
          #  db.func.sum(Challenges.value).label("score"),
           # db.func.max(Solves.id).label("id"),
            #db.func.max(Solves.date).label("date"),
        #)
        #.join(Challenges)
        #.filter(Challenges.value != 0)
        #.group_by(Solves.account_id)
    #)

    badges_entries = (
        db.session.query(
            BadgesEntries.user_id.label("user_id"),
            ##db.func.sum(BadgesEntries.value).label("score"),
            db.func.max(BadgesEntries.id).label("id"),
            db.func.max(BadgesEntries.date).label("date"),
            db.func.max(BadgesEntries.badge_id).label("badge_id"),
        )

        .group_by(BadgesEntries.user_id)
    )

    """
    Filter out solves and awards that are before a specific time point.
    """
    freeze = get_config("freeze")
    if not admin and freeze:
    
        badges_entries = badges_entries.filter(BadgesEntries.date < unix_time_to_utc(freeze))

    """
    Combine awards and solves with a union. They should have the same amount of columns
    """
    results = union_all(badges_entries).alias("results")

    """
    Sum each of the results by the team id to get their score.
    
    sumscores = (
        db.session.query(
            results.columns.account_id,
            db.func.sum(results.columns.score).label("score"),
            db.func.max(results.columns.id).label("id"),
            db.func.max(results.columns.date).label("date"),
        )
        .group_by(results.columns.account_id)
        .subquery()
    )
    """
    """
    Admins can see scores for all users but the public cannot see banned users.

    Filters out banned users.
    Properly resolves value ties by ID.

    Different databases treat time precision differently so resolve by the row ID instead.
    """
    if admin:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                Model.hidden,
                Model.banned,
                #sumscores.columns.score,
                *fields,
            )
            #.join(sumscores, Model.id == sumscores.columns.account_id)
            #.order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Model.id.label("account_id"),
                Model.oauth_id.label("oauth_id"),
                Model.name.label("name"),
                #sumscores.columns.score,
                *fields,
            )
            #.join(sumscores, Model.id == sumscores.columns.account_id)
            .filter(Model.banned == False, Model.hidden == False)
            #.order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings


@cache.memoize(timeout=60)
def get_team_standings(count=None, admin=False, fields=[]):
    """
    scores = (
        db.session.query(
            Solves.team_id.label("team_id"),
            db.func.sum(Challenges.value).label("score"),
            db.func.max(Solves.id).label("id"),
            db.func.max(Solves.date).label("date"),
        )
        .join(Challenges)
        .filter(Challenges.value != 0)
        .group_by(Solves.team_id)
    )
"""





@cache.memoize(timeout=60)
def get_user_standings(count=None, admin=False, fields=[]):
    """
    scores = (
        db.session.query(
            Solves.user_id.label("user_id"),
            #db.func.sum(Challenges.value).label("score"),
            db.func.max(Solves.id).label("id"),
            db.func.max(Solves.date).label("date"),
        )
        .join(Challenges)
        #.filter(Challenges.value != 0)
        .group_by(Solves.user_id)
    )
"""
    badges_entries = (
        db.session.query(
            BadgesEntries.user_id.label("user_id"),
            #db.func.sum(BadgesEntries.value).label("score"),
            db.func.max(BadgesEntries.id).label("id"),
            #db.func.max(BadgesEntries.date).label("date"),
        )
        #.filter(BadgesEntries.value != 0)
        .group_by(BadgesEntries.user_id)
    )

    freeze = get_config("freeze")
    if not admin and freeze:
        #scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
        badges_entries = badges_entries.filter(BadgesEntries.date < unix_time_to_utc(freeze))

    #results = union_all(scores, awards).alias("results")
    """
    sumscores = (
        db.session.query(
            results.columns.user_id,
            db.func.sum(results.columns.score).label("score"),
            db.func.max(results.columns.id).label("id"),
            db.func.max(results.columns.date).label("date"),
        )
        .group_by(results.columns.user_id)
        .subquery()
    )
    """

    if admin:
        standings_query = (
            db.session.query(
                Users.id.label("user_id"),
                Users.oauth_id.label("oauth_id"),
                Users.name.label("name"),
                Users.hidden,
                Users.banned,
                #sumscores.columns.score,
                *fields,
            )
            #.join(sumscores, Users.id == sumscores.columns.user_id)
            #.order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )
    else:
        standings_query = (
            db.session.query(
                Users.id.label("user_id"),
                Users.oauth_id.label("oauth_id"),
                Users.name.label("name"),
                #sumscores.columns.score,
                *fields,
            )
            #.join(sumscores, Users.id == sumscores.columns.user_id)
            .filter(Users.banned == False, Users.hidden == False)
            #.order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        )

    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()

    return standings
