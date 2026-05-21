# GraphQL Mode

From SQLModel entities to a complete GraphQL API — SDL auto-generation, automatic relationship resolution, and DataLoader batch loading.

## GraphQLHandler Configuration

```python
from nexusx import GraphQLHandler

handler = GraphQLHandler(
    base=SQLModel,          # SQLModel base class for auto-discovering entities
    session_factory=async_session,  # Async session factory (required)
)
```

`session_factory` is required — DataLoader needs it to execute batch queries.

## @query and @mutation Decorators

Mark query and mutation methods on SQLModel entities:

```python
from nexusx import query, mutation

class Post(SQLModel, table=True):
    # ... field definitions ...

    @query
    async def get_all(cls, limit: int = 10) -> list['Post']:
        async with get_session() as session:
            return (await session.exec(select(cls).limit(limit))).all()

    @mutation
    async def create(cls, title: str, author_id: int) -> 'Post':
        async with get_session() as session:
            post = cls(title=title, author_id=author_id)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
```

### Field Naming Convention

`@query` / `@mutation` methods auto-generate GraphQL field names: `{EntityName}{MethodName}`

| Entity | Method | GraphQL Field |
|--------|--------|---------------|
| `Post` | `get_all` | `postGetAll` |
| `Post` | `create` | `postCreate` |
| `User` | `get_by_id` | `userGetById` |

### Method Definition Rules

- The first parameter must be `cls` (the decorator converts it to a classmethod)
- The method's docstring becomes the GraphQL field description
- `query_meta` parameters do not appear in the SDL (internal mechanism)

## Entity Discovery Rules

1. SQLModel subclasses with `@query` or `@mutation` are auto-discovered
2. Relationship-associated entities of discovered entities are recursively included
3. Entities without decorators and without relationship references are not included in the schema

## Automatic Relationship Resolution

The framework traverses the GraphQL selection tree, collects FK values layer by layer, and batch-loads relationships via DataLoader:

```graphql
{
  postGetAll(limit: 5) {
    id
    title
    author { name email }
  }
}
```

Execution process:

1. Execute the `postGetAll` query, fetching 5 Posts
2. Collect all `author_id` values, query Users in one batch via DataLoader
3. Map Users back to their corresponding Posts

**No matter how many results, each relationship executes only one query.**

### Supported Relationship Types

- `MANYTOONE`: Post → User (via FK)
- `ONETOMANY`: User → Posts (via Relationship)
- `MANYTOMANY`: Requires an intermediate table

## GraphiQL Integration

```python
@app.get("/graphql", response_class=HTMLResponse)
async def graphiql():
    return handler.get_graphiql_html()
```

Provides a complete GraphiQL interactive query interface.

## Execution Flow

```
GraphQL query string
  → QueryParser parses into FieldSelection tree
  → Execute root fields (@query methods)
  → Traverse selection tree layer by layer
  → Collect FK values, DataLoader batch loads
  → Assemble response JSON
```

## Next Steps

- [GraphQL Pagination](./graphql_pagination.md) — Pagination support for list relationships
- [Auto Query](./graphql_auto_query.md) — Skip @query, auto-generate by_id / by_filter
- [Core API Mode](./core_api.md) — REST response building outside of GraphQL
