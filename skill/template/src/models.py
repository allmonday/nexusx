"""Phase 1→2: SQLModel entity definitions.

Phase 1: Entity skeleton + Relationship + @query/@mutation (pass + docstring).
Phase 2: Complete method implementations with SQLAlchemy async.

Entity graph:
    Sprint ──1:N──→ Task ──N:1──→ User
"""
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, select

from sqlmodel_nexus import mutation, query

from src.database import async_session


class BaseEntity(SQLModel):
    """All entities inherit from this base class for shared metadata discovery."""


class User(BaseEntity, table=True):
    """系统用户，可以是任务的创建者或负责人。"""

    id: int | None = Field(default=None, primary_key=True, description="用户唯一标识")
    name: str = Field(description="用户显示名称")

    # ORM relationships
    tasks: list["Task"] = Relationship(back_populates="owner")

    @query
    async def get_users(cls) -> list["User"]:
        """获取所有用户。"""
        async with async_session() as session:
            result = await session.exec(select(cls))
            return list(result.all())

    @mutation
    async def create_user(cls, name: str) -> "User":
        """创建新用户。"""
        async with async_session() as session:
            user = cls(name=name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user


class Sprint(BaseEntity, table=True):
    """迭代周期，包含一批待完成的任务。"""

    id: int | None = Field(default=None, primary_key=True, description="Sprint 唯一标识")
    name: str = Field(description="Sprint 名称，如 'Sprint 1'")

    # ORM relationships
    tasks: list["Task"] = Relationship(
        back_populates="sprint",
        sa_relationship_kwargs={"order_by": "Task.id"},
    )

    @query
    async def get_sprints(cls) -> list["Sprint"]:
        """获取所有 Sprint。"""
        async with async_session() as session:
            result = await session.exec(select(cls))
            return list(result.all())

    @mutation
    async def create_sprint(cls, name: str) -> "Sprint":
        """创建新 Sprint。"""
        async with async_session() as session:
            sprint = cls(name=name)
            session.add(sprint)
            await session.commit()
            await session.refresh(sprint)
            return sprint


class Task(BaseEntity, table=True):
    """具体的工作项，属于某个 Sprint，由某个 User 负责。"""

    id: int | None = Field(default=None, primary_key=True, description="任务唯一标识")
    title: str = Field(description="任务标题")
    done: bool = Field(default=False, description="是否已完成")

    sprint_id: int = Field(foreign_key="sprint.id", description="所属 Sprint ID")
    owner_id: int | None = Field(default=None, foreign_key="user.id", description="负责人 ID，可为空表示未分配")

    # ORM relationships
    sprint: Optional["Sprint"] = Relationship(back_populates="tasks")
    owner: Optional["User"] = Relationship()

    @query
    async def get_tasks(cls) -> list["Task"]:
        """获取所有任务。"""
        async with async_session() as session:
            result = await session.exec(select(cls))
            return list(result.all())

    @mutation
    async def create_task(cls, title: str, sprint_id: int, owner_id: int | None = None) -> "Task":
        """在指定 Sprint 中创建新任务。"""
        async with async_session() as session:
            task = cls(title=title, sprint_id=sprint_id, owner_id=owner_id)
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task


# ── ErManager + Resolver (Phase 3) ──────────────────────────────────────

from sqlmodel_nexus import ErManager  # noqa: E402

er = ErManager(
    entities=[User, Sprint, Task],
    session_factory=async_session,
)
Resolver = er.create_resolver()
