# Core API Mode

The Core API mode is for scenarios beyond GraphQL — FastAPI REST endpoints, service layer response assembly, or any use-case DTO. Same DataLoader batch loading, same N+1 prevention.

> **Prerequisites**: SQLModel entities defined with `Relationship` / `Field(foreign_key=...)`.
>
> **Live demo**: See [`demo/core_api/`](https://github.com/allmonday/sqlmodel-nexus/tree/master/demo/core_api) for a complete REST server with Sprint/Task/User models. The DTOs in [`dtos.py`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py) progress through 5 levels of complexity.

Core concepts progress in order: **Implicit auto-loading → resolve\_\* → post\_\* → Cross-layer data flow**.

## Step 1: DefineSubset + Implicit Auto-Loading

The simplest Core API usage: select fields from SQLModel entities, declare relationship fields — they load automatically.

```python
from sqlmodel import SQLModel, select
from sqlmodel_nexus import DefineSubset, ErManager

class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None   # Name matches Task.owner relationship → auto-loaded

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    tasks: list[TaskDTO] = []      # Name matches Sprint.tasks relationship → auto-loaded
```

> ⬆ This is **Level 2** in the demo's [`dtos.py`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py#L30).

## ErManager Initialization

```python
# At application startup — execute once
er = ErManager(base=SQLModel, session_factory=async_session)
Resolver = er.create_resolver()
```

- `ErManager` discovers all SQLModel entities and their ORM relationships
- `create_resolver()` returns a Resolver class bound to the entity graph

**Note**: `base` and `entities` parameters are mutually exclusive — you cannot pass both.

## Using in FastAPI

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/sprints")
async def get_sprints():
    async with async_session() as session:
        sprints = (await session.exec(select(Sprint))).all()
    dtos = [SprintDTO(**s.model_dump()) for s in sprints]
    return await Resolver().resolve(dtos)  # tasks + owner auto-loaded
```

> **Tip**: For more efficient field-selective queries, use `build_dto_select(SprintDTO)` — it generates a SQLAlchemy select() that only fetches the fields declared in `__subset__`. See [`demo/core_api/dtos.py` → `TaskService.list_tasks`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/use_case/mcp_server.py#L63).

## How Auto-Loading Works

Implicit auto-loading triggers when **all** conditions are true:

1. The field has no corresponding `resolve_*` method
2. The field is an extra field (not in `__subset__` fields)
3. The field name matches a registered ORM or custom relationship
4. The field type is a DefineSubset DTO compatible with the relationship target

## Next Steps

- [Core API Advanced](./core_api_advanced.md) — resolve_*, post_*, cross-layer data flow
- [Custom Relationships](./custom_relationship.md) — non-ORM relationships
- [UseCase Service](../advanced/use_case_service.md) — wrap Core API DTOs in business services
