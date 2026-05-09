"""Sprint UseCaseService — sprint management with task statistics."""
from sqlmodel_nexus import UseCaseService, build_dto_select, query

from src.database import async_session
from src.models import Resolver, Sprint
from src.service.sprint.dtos import SprintSummary


class SprintService(UseCaseService):
    """Sprint management with task statistics."""

    @query
    async def list_sprints(cls) -> list[SprintSummary]:
        """Get all sprints with task counts and contributor names."""
        stmt = build_dto_select(SprintSummary)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [SprintSummary(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

    @query
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        """Get a single sprint by ID."""
        stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        if not rows:
            return None
        dto = SprintSummary(**dict(rows[0]._mapping))
        return await Resolver().resolve(dto)
