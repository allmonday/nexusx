# GraphQL 模式

从 SQLModel 实体到完整的 GraphQL API——SDL 自动生成、关系自动解析、DataLoader 批量加载。

## GraphQLHandler 配置

```python
from sqlmodel_nexus import GraphQLHandler

handler = GraphQLHandler(
    base=SQLModel,          # SQLModel 基类，用于自动发现实体
    session_factory=async_session,  # 异步 session 工厂（必须提供）
)
```

`session_factory` 是必需的——DataLoader 需要它来执行批量查询。

## @query 和 @mutation 装饰器

在 SQLModel 实体上标记查询和变更方法：

```python
from sqlmodel_nexus import query, mutation

class Post(SQLModel, table=True):
    # ... 字段定义 ...

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

### 字段命名规则

`@query` / `@mutation` 方法自动生成 GraphQL 字段名：`{EntityName}{MethodName}`

| 实体 | 方法 | GraphQL 字段 |
|------|------|-------------|
| `Post` | `get_all` | `postGetAll` |
| `Post` | `create` | `postCreate` |
| `User` | `get_by_id` | `userGetById` |

### 方法定义规则

- 第一个参数必须是 `cls`（装饰器会将其转为 classmethod）
- 方法标注的 docstring 会成为 GraphQL 字段的描述
- `query_meta` 参数不出现在 SDL 中（内部机制）

## 实体发现规则

1. 有 `@query` 或 `@mutation` 的 SQLModel 子类会被自动发现
2. 被发现的实体的 Relationship 关联实体也会被递归纳入
3. 没有装饰器且没有关系引用的实体不会被纳入 schema

## 关系自动解析

框架遍历 GraphQL 选择树，逐层收集 FK 值，通过 DataLoader 批量加载关系：

```graphql
{
  postGetAll(limit: 5) {
    id
    title
    author { name email }
  }
}
```

执行过程：

1. 执行 `postGetAll` 查询，获取 5 条 Post
2. 收集所有 `author_id`，通过 DataLoader 一次性查询 User
3. 将 User 映射回对应的 Post

**无论结果有多少条，每个关系只执行一次查询。**

### 支持的关系类型

- `MANYTOONE`：Post → User（通过 FK）
- `ONETOMANY`：User → Posts（通过 Relationship）
- `MANYTOMANY`：需要中间表

## GraphiQL 集成

```python
@app.get("/graphql", response_class=HTMLResponse)
async def graphiql():
    return handler.get_graphiql_html()
```

提供完整的 GraphiQL 交互式查询界面。

## 执行流程

```
GraphQL 查询字符串
  → QueryParser 解析为 FieldSelection 树
  → 执行根字段（@query 方法）
  → 逐层遍历选择树
  → 收集 FK 值，DataLoader 批量加载
  → 组装响应 JSON
```

## 下一步

- [GraphQL 分页](./graphql_pagination.zh.md) — 列表关系的分页支持
- [自动查询](./graphql_auto_query.zh.md) — 跳过 @query，自动生成 by_id / by_filter
- [Core API 模式](./core_api.zh.md) — GraphQL 之外的 REST 响应构建
