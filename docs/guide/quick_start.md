# Quick Start

Pick your path — three ways to use sqlmodel-nexus from the same SQLModel entities.

All paths assume you have:

```bash
pip install sqlmodel-nexus
```

---

## 🟣 Path 1: GraphQL API

Define entities, add `@query` / `@mutation`, create a `GraphQLHandler` — done.

```python
from sqlmodel import SQLModel, Field, Relationship, select
from sqlmodel_nexus import query, mutation, GraphQLHandler

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    posts: list["Post"] = Relationship(back_populates="author")

    @query
    async def get_all(cls, limit: int = 10) -> list["User"]:
        async with get_session() as session:
            return (await session.exec(select(cls).limit(limit))).all()

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="user.id")
    author: User | None = Relationship(back_populates="posts")

    @mutation
    async def create(cls, title: str, author_id: int) -> "Post":
        async with get_session() as session:
            post = cls(title=title, author_id=author_id)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

handler = GraphQLHandler(base=SQLModel, session_factory=async_session)
```

```graphql
# Query
{ userGetAll(limit: 5) { id name posts { title } } }

# Mutation
mutation { postCreate(title: "Hello", authorId: 1) { id title } }
```

📖 Learn more: [GraphQL Mode](./guide/graphql_mode.md)

---

## 🟢 Path 2: REST API (Core API)

Define `DefineSubset` DTOs — relationship fields auto-load via DataLoader.

```python
from sqlmodel_nexus import DefineSubset, ErManager

# 1. Define DTOs
class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))

class PostDTO(DefineSubset):
    __subset__ = (Post, ("id", "title", "author_id"))
    author: UserDTO | None = None    # auto-loaded! No resolve_* needed

# 2. Create Resolver
er = ErManager(base=SQLModel, session_factory=async_session)
Resolver = er.create_resolver()

# 3. In your FastAPI endpoint
@app.get("/posts")
async def get_posts():
    posts = (await session.exec(select(Post).limit(10))).all()
    dtos = [PostDTO(**p.model_dump()) for p in posts]    # or use build_dto_select
    return await Resolver().resolve(dtos)                 # resolves author automatically
```

Output JSON:

```json
[
  { "id": 1, "title": "Hello", "author": { "id": 1, "name": "Alice" } },
  { "id": 2, "title": "World", "author": { "id": 2, "name": "Bob" } }
]
```

📖 Learn more: [Core API Mode](./guide/core_api.md)

---

## 🟡 Path 3: MCP for AI Agents (UseCase)

Write business logic once — serve both MCP and FastAPI from the same `UseCaseService` class.

```python
from sqlmodel_nexus import UseCaseService, UseCaseAppConfig, create_use_case_mcp_server

class PostService(UseCaseService):
    @query
    async def list_posts(cls, limit: int = 10) -> list[PostDTO]:
        stmt = build_dto_select(PostDTO)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [PostDTO(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

mcp = create_use_case_mcp_server(apps=[
    UseCaseAppConfig(name="blog", services=[PostService]),
])
mcp.run()  # AI agents can: list_apps → list_services → describe_service → call
```

📖 Learn more: [UseCase Service](./advanced/use_case_service.md) | [FastAPI Integration](./advanced/use_case_fastapi.md)

---

## What's Next

| Topic | Guide |
|-------|-------|
| How DTOs auto-load relationships | [Core API Mode](./guide/core_api.md) |
| Derived fields via `post_*` | [Core API Advanced](./guide/core_api_advanced.md) |
| Pagination in GraphQL | [GraphQL Pagination](./guide/graphql_pagination.md) |
| Non-ORM relationships | [Custom Relationships](./guide/custom_relationship.md) |
| Five-level progressive demo | [`demo/core_api/dtos.py`](../demo/core_api/dtos.py) |
| Full project template | [`skill/template/`](../skill/template/) |

The remaining guides and API references are listed in the [index](index.md).
