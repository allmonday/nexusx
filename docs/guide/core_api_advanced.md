# Core API Advanced

When implicit auto-loading is not enough, Core API provides three progressive capabilities: `resolve_*` for custom loading, `post_*` for derived field computation, and cross-layer data flow.

## resolve_*: Custom Loading

When the field name doesn't match a relationship, or custom logic is needed, use `resolve_*`:

```python
from nexusx import Loader

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

### ExposeAs: Ancestor → Descendant

```python
from typing import Annotated
from nexusx import ExposeAs

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    name: Annotated[str, ExposeAs('sprint_name')]  # Expose to descendants
    tasks: list[TaskDTO] = []
```

### SendTo + Collector: Descendant → Ancestor

```python
from nexusx import SendTo, Collector

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    name: Annotated[str, ExposeAs('sprint_name')]
    tasks: list[TaskDTO] = []
    contributors: list[UserDTO] = []

    def post_contributors(self, collector=Collector('contributors')):
        return collector.values()  # Collect values sent by descendants

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: Annotated[UserDTO | None, SendTo('contributors')] = None  # Send to ancestor
    full_title: str = ""

    def post_full_title(self, ancestor_context):
        return f"{ancestor_context['sprint_name']} / {self.title}"
```

Applicable scenarios:

- Child nodes need ancestor context (sprint name, permission info, tenant configuration)
- Parent nodes need to aggregate results from multiple descendants (contributors, tags)

## Resolver Options

```python
result = await Resolver(
    context={"user_id": 42},     # Pass global context
    loader_params={},            # DataLoader extra parameters
).resolve(dtos)
```

## Loader Dependency Name Rule

`Loader('author')` requires a relationship named `author` in ErManager. When using implicit auto-loading, you typically don't need to write Loaders manually.

## Next Steps

- [Custom Relationships](./custom_relationship.md) — Non-ORM relationship declarations
- [MCP Service](../advanced/mcp_service.md) — Expose APIs to AI agents
