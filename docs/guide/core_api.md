# Core API Mode

The Core API mode is for scenarios beyond GraphQL — FastAPI REST endpoints, service layer response assembly, or any use-case DTO. Same DataLoader batch loading, same N+1 prevention.

Core concepts progress in order: **Implicit auto-loading → resolve_\* → post_\* → Cross-layer data flow**.

## Step 1: DefineSubset + Implicit Auto-Loading

The simplest Core API usage: select fields from SQLModel entities, declare relationship fields — they load automatically.

```python
from sqlmodel import SQLModel, select
from nexusx import DefineSubset, ErManager

class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None   # Name matches Task.owner relationship → auto-loaded

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    tasks: list[TaskDTO] = []      # Name matches Sprint.tasks relationship → auto-loaded
```

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
    dtos = [SprintDTO(id=s.id, name=s.name) for s in sprints]
    return await Resolver().resolve(dtos)
```

## Four Conditions for Implicit Auto-Loading

The Resolver automatically loads relationship fields (no need to write `resolve_*`) when all conditions are met:

1. The field has no corresponding `resolve_*` method
2. The field is an extra field (not in the `__subset__` definition)
3. The field name matches a registered ORM/custom relationship
4. The field type is a BaseModel DTO compatible with the relationship target entity

## DefineSubset Rules

- `__subset__` accepts a tuple `(Entity, ('field1', 'field2'))`
- FK fields (e.g., `owner_id`) are automatically hidden from serialization output, but remain internally accessible in `resolve_*`
- Relationship fields are declared in the class body (not in `__subset__`), and must use DTO types

## How It Works

```
SprintDTO(id=1, name="Sprint 1")
  → Implicit auto-load: tasks → [TaskDTO(...), TaskDTO(...)]
    → Each TaskDTO: Implicit auto-load: owner → UserDTO(...)
  → Result: complete nested response tree
```

Each relationship executes only one DataLoader query, regardless of how many Sprints or Tasks exist.

## DTO Type Constraint

```python
# Wrong — direct use of SQLModel entity is prohibited
class TaskDTO(DefineSubset):
    owner: User | None = None  # TypeError!

# Correct — use DTO type
class TaskDTO(DefineSubset):
    owner: UserDTO | None = None  # OK
```

## Next Steps

- [Core API Advanced](./core_api_advanced.md) — resolve_*/post_*/cross-layer data flow
- [Custom Relationships](./custom_relationship.md) — Non-ORM relationship declarations
