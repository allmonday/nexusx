# 快速开始

30 秒内从 SQLModel 实体到可运行的 GraphQL API。

## 安装

```bash
pip install nexusx
```

## 1. 定义 SQLModel 实体

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

## 2. 添加 @query 和 @mutation

```python
from nexusx import query, mutation

class Post(SQLModel, table=True):
    # ... 字段同上 ...

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

## 3. 创建 GraphQLHandler

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

## 4. 启动并查询

```bash
uvicorn app:app
# 访问 http://localhost:8000/graphql
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

**关系自动解析**：框架遍历 GraphQL 选择树，逐层收集 FK 值并通过 DataLoader 批量加载。无论返回多少条记录，每个关系只需一次查询。

## 核心心智模型

```
SQLModel 实体 + @query 装饰器 → GraphQL API（SDL + DataLoader 自动生成）
```

接下来，了解 [GraphQL 模式](./graphql_mode.zh.md) 的完整能力。
