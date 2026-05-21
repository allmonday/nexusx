# Custom Relationships

For relationships that don't exist in the ORM — cross-service calls, computed edges, non-database sources — use `Relationship` to declare them on entities.

## Why Custom Relationships

In standard scenarios, SQLModel's `Relationship` and `Field(foreign_key=...)` already cover database-level relationships. However, the following scenarios require custom declarations:

- **Cross-service calls**: Load associated data from external APIs
- **Computed edges**: Associations based on business logic rather than FKs
- **Non-database sources**: Caches, search engines, file systems

## Declaration

Declare in the `__relationships__` list on SQLModel entities:

```python
from nexusx import Relationship

async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    """Batch load tags."""
    async with get_session() as session:
        stmt = (
            select(Tag, TaskTag.task_id)
            .join(TaskTag)
            .where(TaskTag.task_id.in_(task_ids))
        )
        rows = (await session.exec(stmt)).all()
        return build_list(rows, task_ids, lambda row: row[1], lambda row: row[0])

class Task(SQLModel, table=True):
    __relationships__ = [
        Relationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
    ]
    id: int | None = Field(default=None, primary_key=True)
    title: str
```

## Relationship Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fk` | `str` | Field name on the source entity used by DataLoader to collect key values |
| `target` | `type` | Target type (`Entity` or `list[Entity]`) |
| `name` | `str` | Relationship name, used for field matching during implicit auto-loading |
| `loader` | `type` or `callable` | DataLoader class or async batch function |

### target Syntax

```python
# Single target
Relationship(fk="owner_id", target=User, name="owner", loader=user_loader)

# List target
Relationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
```

## Integration with Implicit Auto-Loading

Custom relationships use the same auto-loading mechanism as ORM relationships:

```python
class TagDTO(DefineSubset):
    __subset__ = (Tag, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title"))
    tags: list[TagDTO] = []   # Name "tags" matches custom relationship → auto-loaded
```

As long as the four conditions for implicit auto-loading are met, custom relationships are handled automatically.

## DataLoader Batch Functions

The `loader` can be a DataLoader class or an async batch function. Batch functions receive a list of key values and return corresponding results:

```python
# Single target (fk → single entity)
async def user_loader(user_ids: list[int]) -> dict[int, User]:
    users = await fetch_users(user_ids)
    return {u.id: u for u in users}

# List target (fk → entity list)
async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    tags = await fetch_tags_for_tasks(task_ids)
    return group_by_task(tags, task_ids)
```

## Next Steps

- [ER Diagram](./er_diagram.md) — Visualizing entity relationships
- [Core API Mode](./core_api.md) — Using custom relationships in DTOs
