"""Search service for unified search across players, clubs, competitions, and nations."""

from sqlalchemy import func, literal, select, union_all
from sqlalchemy.orm import Session

from app.models.competitions import Competition
from app.models.nations import Nation
from app.models.player_stats import PlayerStats
from app.models.players import Player
from app.models.teams import Team
from app.schemas.search import SearchResult, SearchType


def search_all(
    db: Session, query: str, limit_per_type: int = 1, type_filter: str | None = None
) -> list[SearchResult]:
    """Search across players, clubs, competitions, and nations with prefix preference.

    Prefix matches (name starts with query) are returned before contains matches.
    Players are sorted by matches played; other types have no specific ordering.

    Args:
        db: Database session
        query: Search query string (lowercased and trimmed)
        limit_per_type: Max results per entity type (default: 1)
        type_filter: Optional filter to restrict results to a specific type.
                    Should be one of SearchType enum values: "Player", "Club",
                    "Competition", or "Nation". If None, searches all types.

    Returns:
        List of SearchResult objects: prefix matches first, then contains matches.
    """
    if not query or not query.strip():
        return []

    query_lower = query.lower().strip()

    if type_filter is not None:
        valid_types = {st.value for st in SearchType}
        if type_filter not in valid_types:
            return []

    matches_played_subquery = (
        select(
            PlayerStats.player_id,
            func.coalesce(func.sum(PlayerStats.matches_played), 0).label("total_matches"),
        )
        .group_by(PlayerStats.player_id)
        .subquery()
    )

    prefix_queries = []
    contains_queries = []

    if type_filter is None or type_filter == SearchType.PLAYER.value:
        prefix_queries.append(
            select(
                Player.id,
                Player.name,
                literal(SearchType.PLAYER.value).label("type"),
                func.coalesce(matches_played_subquery.c.total_matches, 0).label("matches_played"),
            )
            .outerjoin(matches_played_subquery, Player.id == matches_played_subquery.c.player_id)
            .where(func.lower(Player.name).like(f"{query_lower}%"), Player.name.isnot(None))
        )

    if type_filter is None or type_filter == SearchType.CLUB.value:
        prefix_queries.append(
            select(
                Team.id,
                Team.name,
                literal(SearchType.CLUB.value).label("type"),
                literal(0).label("matches_played"),
            ).where(func.lower(Team.name).like(f"{query_lower}%"), Team.name.isnot(None))
        )

    if type_filter is None or type_filter == SearchType.COMPETITION.value:
        prefix_queries.append(
            select(
                Competition.id,
                Competition.name,
                literal(SearchType.COMPETITION.value).label("type"),
                literal(0).label("matches_played"),
            ).where(
                func.lower(Competition.name).like(f"{query_lower}%"), Competition.name.isnot(None)
            )
        )

    if type_filter is None or type_filter == SearchType.NATION.value:
        prefix_queries.append(
            select(
                Nation.id,
                Nation.name,
                literal(SearchType.NATION.value).label("type"),
                literal(0).label("matches_played"),
            ).where(func.lower(Nation.name).like(f"{query_lower}%"))
        )

    if type_filter is None or type_filter == SearchType.PLAYER.value:
        contains_queries.append(
            select(
                Player.id,
                Player.name,
                literal(SearchType.PLAYER.value).label("type"),
                func.coalesce(matches_played_subquery.c.total_matches, 0).label("matches_played"),
            )
            .outerjoin(matches_played_subquery, Player.id == matches_played_subquery.c.player_id)
            .where(
                func.lower(Player.name).like(f"%{query_lower}%"),
                Player.name.isnot(None),
                ~func.lower(Player.name).like(f"{query_lower}%"),
            )
        )

    if type_filter is None or type_filter == SearchType.CLUB.value:
        contains_queries.append(
            select(
                Team.id,
                Team.name,
                literal(SearchType.CLUB.value).label("type"),
                literal(0).label("matches_played"),
            ).where(
                func.lower(Team.name).like(f"%{query_lower}%"),
                Team.name.isnot(None),
                ~func.lower(Team.name).like(f"{query_lower}%"),
            )
        )

    if type_filter is None or type_filter == SearchType.COMPETITION.value:
        contains_queries.append(
            select(
                Competition.id,
                Competition.name,
                literal(SearchType.COMPETITION.value).label("type"),
                literal(0).label("matches_played"),
            ).where(
                func.lower(Competition.name).like(f"%{query_lower}%"),
                Competition.name.isnot(None),
                ~func.lower(Competition.name).like(f"{query_lower}%"),
            )
        )

    if type_filter is None or type_filter == SearchType.NATION.value:
        contains_queries.append(
            select(
                Nation.id,
                Nation.name,
                literal(SearchType.NATION.value).label("type"),
                literal(0).label("matches_played"),
            ).where(
                func.lower(Nation.name).like(f"%{query_lower}%"),
                ~func.lower(Nation.name).like(f"{query_lower}%"),
            )
        )

    prefix_results = []
    contains_results = []

    if prefix_queries:
        prefix_union = union_all(*prefix_queries)
        prefix_rows = db.execute(prefix_union).all()
        prefix_results = list(prefix_rows)
        prefix_results.sort(key=lambda x: -x.matches_played if x.type == "Player" else 0)

    if contains_queries:
        contains_union = union_all(*contains_queries)
        contains_rows = db.execute(contains_union).all()
        contains_results = list(contains_rows)
        contains_results.sort(key=lambda x: -x.matches_played if x.type == "Player" else 0)

    type_counts: dict[str, int] = {}
    results: list[SearchResult] = []

    for row in prefix_results:
        result_type = row.type
        if type_counts.get(result_type, 0) < limit_per_type:
            results.append(SearchResult(id=row.id, name=row.name, type=result_type))
            type_counts[result_type] = type_counts.get(result_type, 0) + 1

    for row in contains_results:
        result_type = row.type
        if type_counts.get(result_type, 0) < limit_per_type:
            results.append(SearchResult(id=row.id, name=row.name, type=result_type))
            type_counts[result_type] = type_counts.get(result_type, 0) + 1

    return results
