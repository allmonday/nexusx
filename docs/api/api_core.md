# Core API Reference

Complete API reference for ErManager, Resolver, DefineSubset, and Loader.

## ErManager

Entity relationship manager — discovers entities, registers relationships, and creates Resolvers.

```python
from nexusx import ErManager

er = ErManager(
    base=SQLModel,                    # SQLModel base class (mutually exclusive with entities)
    entities=None,                    # Explicit entity list (mutually exclusive with base)
    session_factory=async_session,    # Async session factory
)
```

**Note**: `base` and `entities` are mutually exclusive — you cannot pass both.

### Methods

| Method | Description |
|--------|-------------|
| `create_resolver()` | Returns a Resolver class bound to the entity graph |
| `get_diagram()` | Returns an ErDiagram instance |

## Resolver

A class returned by `ErManager.create_resolver()`. Used to resolve DTO trees.

```python
Resolver = er.create_resolver()

result = await Resolver().resolve(dtos)
```

### Resolver Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | `dict` | Global context, accessible via `ancestor_context` |
| `loader_params` | `dict` | DataLoader extra parameters |
| `debug` | `bool` | Enable debug logging |

### Resolver.resolve

```python
result = await Resolver().resolve(dtos)
```

The `dtos` parameter can be a single DTO instance or a list of DTOs. Returns the same objects after in-place modification.

### Execution Order

1. Execute all `resolve_*` methods (load relationship data)
2. Traverse existing object fields
3. Execute all `post_*` methods (compute derived fields)
4. Collect SendTo values to ancestor Collectors

## DefineSubset

DTO base class — generates Pydantic models from SQLModel entities.

```python
from nexusx import DefineSubset

class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))
```

### __subset__ Syntax

Accepts a tuple `(Entity, ('field1', 'field2'))` or a `SubsetConfig` object.

### Rules

- FK fields are automatically hidden from serialization output (`exclude=True`), but remain internally accessible
- Relationship fields are declared in the class body (not in `__subset__`), and must use DTO types
- Direct use of SQLModel entities as field types is prohibited

## SubsetConfig

Declarative DTO configuration (alternative to `__subset__`):

```python
from nexusx import SubsetConfig

class UserDTO(DefineSubset):
    __subset__ = SubsetConfig(entity=User, fields=("id", "name"))
```

## Loader

Declare DataLoader dependencies in `resolve_*` methods.

```python
from nexusx import Loader

# DataLoader class
def resolve_tags(self, loader=Loader(TagLoader)):
    return loader.load(self.id)

# Async batch function
async def load_users(user_ids):
    ...
def resolve_owner(self, loader=Loader(load_users)):
    return loader.load(self.owner_id)
```

**Loader dependency names must match relationship names**: `Loader('author')` requires a relationship named `author` in ErManager.

## build_dto_select

Helper function that builds a SELECT statement for querying DTO fields from the SQL database:

```python
from nexusx import build_dto_select

stmt = build_dto_select(SprintSummary)
stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
```

> **Note:** When ORM relationships use `lazy="noload"` (the recommended pattern with ErManager + Resolver), this function provides minimal benefit since the only pruning is on scalar columns. You can achieve the same result with `select(Entity)` and `DTO.model_validate(entity)`. Use this function when the DTO selects a small subset of scalar columns from a wide table.
