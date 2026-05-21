# Auto Query

Skip the `@query` decorator — the framework auto-generates `by_id` and `by_filter` queries for each entity.

## AutoQueryConfig

```python
from nexusx import GraphQLHandler, AutoQueryConfig

handler = GraphQLHandler(
    base=SQLModel,
    session_factory=async_session,
    auto_query_config=AutoQueryConfig(session_factory=async_session),
)
```

You can also register manually:

```python
from nexusx import add_standard_queries

add_standard_queries(handler, AutoQueryConfig(session_factory=async_session))
```

## by_id: Single Record by Primary Key

Auto-generated for each entity with exactly one primary key field:

```graphql
{ userById(id: 1) { name email } }
{ postById(id: 42) { title author { name } } }
```

## by_filter: Field-based Filtering

Generates a `FilterInput` type and filter query for each entity:

```graphql
{ userByFilter(filter: { name: "Alice" }, limit: 5) { id name email } }
{ postByFilter(filter: { author_id: 1 }, limit: 10) { id title } }
```

The `FilterInput` type fields correspond one-to-one with entity fields (excluding relationship fields), supporting exact-match filtering.

## Limitations

- **by_id only supports single primary keys**: by_id is not generated for composite primary key entities
- **by_filter is exact-match only**: Does not support LIKE, range queries, etc. — only exact field value matching
- **Requires session_factory**: AutoQueryConfig needs its own session_factory parameter

## Coexistence with @query

Auto queries and manual `@query` / `@mutation` can coexist:

```python
class Post(SQLModel, table=True):
    # ... field definitions ...

    @query
    async def get_recent(cls, days: int = 7) -> list['Post']:
        """Custom query — beyond auto-generated queries"""
        ...

handler = GraphQLHandler(
    base=SQLModel,
    session_factory=async_session,
    auto_query_config=AutoQueryConfig(session_factory=async_session),
)
```

The GraphQL schema now contains:
- `postById`, `postByFilter` (auto-generated)
- `postGetRecent` (manually defined)

## Next Steps

- [Core API Mode](./core_api.md) — Declarative DTO building for REST endpoints
- [GraphQL Mode](./graphql_mode.md) — Complete GraphQL capabilities
