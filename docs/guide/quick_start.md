# Quick Start

From SQLModel entities to a working GraphQL API in 30 seconds.

## Installation

```bash
pip install nexusx
```

## 1. Define SQLModel Entities

```python
from sqlmodel import SQLModel, Field, Relationship, select

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    posts: list["Post"] = Relationship(back_populates="author")

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="user.id")
    author: User | None = Relationship(back_populates="posts")
```

## 2. Add @query and @mutation

```python
from nexusx import query, mutation

class Post(SQLModel, table=True):
    # ... fields as above ...

    @query
    async def get_all(cls, limit: int = 10) -> list['Post']:
        """Get all posts."""
        async with get_session() as session:
            return (await session.exec(select(cls).limit(limit))).all()

    @mutation
    async def create(cls, title: str, author_id: int) -> 'Post':
        """Create a new post."""
        async with get_session() as session:
            post = cls(title=title, author_id=author_id)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
```

## 3. Create GraphQLHandler

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from nexusx import GraphQLHandler

handler = GraphQLHandler(base=SQLModel, session_factory=async_session)

class GraphQLRequest(BaseModel):
    query: str

app = FastAPI()

@app.get("/graphql", response_class=HTMLResponse)
async def graphiql():
    return handler.get_graphiql_html()

@app.post("/graphql")
async def graphql(req: GraphQLRequest):
    return await handler.execute(req.query)
```

## 4. Run and Query

```bash
uvicorn app:app
# Visit http://localhost:8000/graphql
```

```graphql
{
  postGetAll(limit: 5) {
    id
    title
    author { name email }
  }
}
```

**Automatic relationship resolution**: The framework traverses the GraphQL selection tree, collects FK values layer by layer, and batch-loads relationships via DataLoader. No matter how many records are returned, each relationship requires only one query.

## Core Mental Model

```
SQLModel entities + @query decorators → GraphQL API (SDL + DataLoader auto-generated)
```

Next, learn about the full capabilities of [GraphQL Mode](./graphql_mode.md).
