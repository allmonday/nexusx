# GraphQLHandler API

Core entry point for GraphQL mode — SDL generation, query execution, and GraphiQL integration.

## GraphQLHandler

```python
from nexusx import GraphQLHandler

handler = GraphQLHandler(
    base=SQLModel,                    # SQLModel base class (auto-discover entities)
    session_factory=async_session,    # Async session factory (required)
    enable_pagination=False,          # Enable list relationship pagination
    auto_query_config=None,           # AutoQueryConfig for auto queries
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | `type` | — | SQLModel base class for auto-discovering entities |
| `session_factory` | `Callable` | — | Async session factory function |
| `enable_pagination` | `bool` | `False` | Enable list relationship pagination |
| `auto_query_config` | `AutoQueryConfig` | `None` | Auto query configuration |

### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute` | `async execute(query: str, context: dict = None) -> dict` | Execute a GraphQL query |
| `get_graphiql_html` | `get_graphiql_html(endpoint: str = "/graphql") -> str` | Get GraphiQL HTML |

## @query Decorator

```python
from nexusx import query

class Post(SQLModel, table=True):
    @query
    async def get_all(cls, limit: int = 10) -> list['Post']:
        """Get all posts."""
        ...
```

- Automatically converted to classmethod
- Docstring becomes the GraphQL field description
- First parameter must be `cls`
- `query_meta` parameters do not appear in the SDL

## @mutation Decorator

```python
from nexusx import mutation

class Post(SQLModel, table=True):
    @mutation
    async def create(cls, title: str, author_id: int) -> 'Post':
        """Create a new post."""
        ...
```

Same rules as `@query`.

## AutoQueryConfig

```python
from nexusx import AutoQueryConfig

config = AutoQueryConfig(session_factory=async_session)
```

Auto-generates `by_id` and `by_filter` queries for all entities. Requires entities to have exactly one primary key field.

## QueryParser

Parses GraphQL query strings into `FieldSelection` trees. Typically not used directly.

## FieldSelection

Query parsing result type, representing a field and its sub-selections in a GraphQL selection set.

## add_standard_queries

Manually register auto queries to an existing GraphQLHandler:

```python
from nexusx import add_standard_queries

add_standard_queries(handler, AutoQueryConfig(session_factory=async_session))
```
