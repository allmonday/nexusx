# Core API Advanced

When implicit auto-loading is not enough, Core API provides three progressive capabilities: `resolve_*` for custom loading, `post_*` for derived field computation, and cross-layer data flow.

> **Prerequisites**: [Core API Mode](./core_api.md) — specifically DefineSubset, ErManager, and implicit auto-loading.
>
> **Live demo**: The advanced concepts below correspond to Levels 3–5 in [`demo/core_api/dtos.py`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py).

## resolve_*: Custom Loading

When the field name doesn't match a relationship, or custom logic is needed, use `resolve_*`:

```python
from sqlmodel_nexus import Loader

async def comments_loader(task_ids: list[int]) -> list[list[Comment]]:
    """Batch load comments for multiple tasks."""
    ...

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None          # Implicit — matches Task.owner
    comments: list[CommentDTO] = []       # Custom — no matching relationship
    comment_count: int = 0

    def resolve_comments(self, loader=Loader(comments_loader)):
        """Load comments via a custom batch function."""
        return loader.load(self.id)
```

`Loader` accepts two forms:

```python
# DataLoader class
def resolve_tags(self, loader=Loader(TagLoader)):
    return loader.load(self.id)

# Async batch function
async def load_permissions(user_ids):
    ...
def resolve_permissions(self, loader=Loader(load_permissions)):
    return loader.load(self.owner_id)
```

**Mental model**: `resolve_*` means "this field needs data from outside the current node".

## post_*: Derived Fields

`post_*` executes after all `resolve_*` and auto-loading in the current subtree is complete. Use it for counting, aggregation, formatting — any computation that depends on already-loaded data.

```python
class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    tasks: list[TaskDTO] = []
    task_count: int = 0
    contributor_names: list[str] = []

    def post_task_count(self):
        return len(self.tasks)

    def post_contributor_names(self):
        return sorted({t.owner.name for t in self.tasks if t.owner})
```

> ⬆ This is **Level 3** in the demo: [`SprintSummary`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py#L53).

Execution order:

1. Implicit auto-loading → `tasks` populated with TaskDTO list
2. Each TaskDTO → Implicit auto-loading → `owner` populated
3. `post_task_count` → `len(self.tasks)`
4. `post_contributor_names` → Extracts deduplicated owner names

### resolve_* vs post_*

| Question | `resolve_*` | `post_*` |
|----------|-------------|----------|
| Needs external IO? | Yes | Usually not |
| Are descendant nodes ready? | No | Yes |
| Suitable for counting, summing, tagging? | Sometimes | Very suitable |
| Will return value continue to be recursively resolved? | Yes | No |

## Cross-layer Data Flow

Use when parent and child nodes need cross-layer collaboration. Only necessary when the tree structure truly matters.

**Key tools**:

- `ExposeAs`: Parent exposes a value to all descendants via `ancestor_context`
- `SendTo`: Child sends a value upward to ancestor Collector
- `Collector`: Aggregates all values sent via SendTo

```python
from sqlmodel_nexus import Collector, DefineSubset, SubsetConfig

class TaskDTO(DefineSubset):
    __subset__ = SubsetConfig(
        kls=Task, fields=["id", "title"],
        send_to=[("owner", "contributors")],   # Send owner to ancestor collector
    )
    owner: UserDTO | None = None

    def post_full_title(self, ancestor_context=None):
        sprint_name = (ancestor_context or {}).get("sprint_name", "unknown")
        return f"{sprint_name} / {self.title}"

class SprintDTO(DefineSubset):
    __subset__ = SubsetConfig(
        kls=Sprint, fields=["id", "name"],
        expose_as=[("name", "sprint_name")],   # Expose name to descendants
    )
    tasks: list[TaskDTO] = []
    contributors: list[UserDTO] = []

    def post_contributors(self, collector=Collector("contributors")):
        return collector.values()
```

> ⬆ This is **Level 4** in the demo: [`SprintDetail`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py#L107).

## Custom Non-ORM Relationships

For data sources that don't use ORM relationships (external APIs, caches, computed edges), declare custom `Relationship` on SQLModel entities with a hand-written async loader:

```python
from sqlmodel_nexus import Relationship as CustomRelationship

async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    async with get_session() as session:
        stmt = select(Tag, TaskTag.task_id).join(TaskTag).where(TaskTag.task_id.in_(task_ids))
        rows = (await session.exec(stmt)).all()
        return build_list(rows, task_ids, lambda r: r[1], lambda r: r[0])

class Task(SQLModel, table=True):
    __relationships__ = [
        CustomRelationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
    ]
```

DTO auto-loads custom relationships the same way as ORM ones:

```python
class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title"))
    tags: list[TagDTO] = []     # Auto-loaded from the custom relationship
```

> ⬆ This is **Level 5** in the demo: [`TaskWithTags`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/core_api/dtos.py#L140).

## Execution Order (Full)

1. Execute all `resolve_*` methods on current node (load relationship data)
2. Traverse existing object/relationship fields recursively (depth-first)
3. Execute all `post_*` methods on current node (compute derived fields)
4. Collect SendTo values upward to ancestor Collectors
