# ER Diagram & Non-ORM Relationships

nexusx auto-discovers ORM relationships from SQLModel entities and supports declaring non-ORM relationships. All relationships can be visualized through ER diagrams.

## ORM Relationship Auto-Discovery

`ErManager` automatically discovers entity relationships from SQLAlchemy metadata:

```python
from nexusx import ErManager

er = ErManager(base=SQLModel, session_factory=async_session)
```

Discovery scope includes:

- SQLModel entity `Relationship` fields
- Foreign keys defined via `Field(foreign_key=...)`
- Bidirectional relationships established through `back_populates`

## Non-ORM Relationship Declaration

For cross-service calls, computed edges, and non-database relationships, use `Relationship` on entities:

```python
from nexusx import Relationship

async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    """Batch load tags for multiple tasks."""
    ...

class Task(SQLModel, table=True):
    __relationships__ = [
        Relationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
    ]
    id: int | None = Field(default=None, primary_key=True)
    title: str
```

### Relationship Parameters

| Parameter | Description |
|-----------|-------------|
| `fk` | FK field name on the source entity (used by DataLoader to collect key values) |
| `target` | Target type (`Entity` or `list[Entity]`) |
| `name` | Relationship name (used for implicit auto-loading matching) |
| `loader` | DataLoader class or async batch function |

## ErManager Initialization

Two mutually exclusive approaches:

```python
# Option 1: Pass a base class, auto-discover all subclasses
er = ErManager(base=SQLModel, session_factory=async_session)

# Option 2: Explicitly pass an entity list
er = ErManager(entities=[Sprint, Task, User], session_factory=async_session)
```

## Custom Relationships + Implicit Auto-Loading

Custom relationships use the same DataLoader infrastructure as ORM relationships and also support implicit auto-loading:

```python
class TagDTO(DefineSubset):
    __subset__ = (Tag, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title"))
    tags: list[TagDTO] = []   # Name matches custom relationship "tags" → auto-loaded
```

## Complete Example

```python
from sqlmodel import SQLModel, Field, Relationship, select
from nexusx import ErManager, DefineSubset

# Entity definitions
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int = Field(foreign_key="user.id")
    owner: User | None = Relationship()

class Sprint(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    tasks: list[Task] = Relationship(back_populates="sprint")

# Initialization
er = ErManager(base=SQLModel, session_factory=async_session)
Resolver = er.create_resolver()
```

## Next Steps

- [ER Diagram Visualization](./er_diagram_visual.md) — Generate Mermaid ER diagrams
- [Custom Relationships](./custom_relationship.md) — Detailed usage of non-ORM relationships
- [Core API Mode](./core_api.md) — Build REST responses with ErManager
