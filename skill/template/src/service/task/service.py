"""Task UseCaseService — task management with auto-loaded owner."""
from sqlmodel_nexus import UseCaseService, build_dto_select, mutation, query
from src.db import async_session
from src.models import Resolver, Task
from src.service.task.dtos import TaskSummary
from src.service.task.methods import create_task as _create_task


class TaskService(UseCaseService):
    """Task management with auto-loaded owner."""

    @query
    async def list_tasks(cls) -> list[TaskSummary]:
        """Get all tasks with their owner (auto-loaded via DataLoader)."""
        stmt = build_dto_select(TaskSummary)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [TaskSummary(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

    @query
    async def get_tasks_by_sprint(cls, sprint_id: int) -> list[TaskSummary]:
        """Get tasks for a specific sprint, with owner auto-loaded."""
        stmt = build_dto_select(TaskSummary, where=Task.sprint_id == sprint_id)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [TaskSummary(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

    @mutation
    async def create_task(cls, title: str, sprint_id: int, owner_id: int | None = None) -> TaskSummary:
        """Create a new task (reuses methods.py function)."""
        task = await _create_task(title=title, sprint_id=sprint_id, owner_id=owner_id)
        dto = TaskSummary(id=task.id, title=task.title, done=task.done)
        return await Resolver().resolve(dto)
