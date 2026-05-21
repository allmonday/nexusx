# 自动查询

跳过 `@query` 装饰器——框架自动为每个实体生成 `by_id` 和 `by_filter` 查询。

## AutoQueryConfig

```python
from nexusx import GraphQLHandler, AutoQueryConfig

handler = GraphQLHandler(
    base=SQLModel,
    session_factory=async_session,
    auto_query_config=AutoQueryConfig(session_factory=async_session),
)
```

也可以手动注册：

```python
from nexusx import add_standard_queries

add_standard_queries(handler, AutoQueryConfig(session_factory=async_session))
```

## by_id：按主键查单个

为每个有且仅有一个主键字段的实体自动生成：

```graphql
{ userById(id: 1) { name email } }
{ postById(id: 42) { title author { name } } }
```

## by_filter：按字段过滤

为每个实体生成 `FilterInput` 类型和过滤查询：

```graphql
{ userByFilter(filter: { name: "Alice" }, limit: 5) { id name email } }
{ postByFilter(filter: { author_id: 1 }, limit: 10) { id title } }
```

`FilterInput` 类型的字段与实体字段一一对应（关系字段除外），支持精确匹配过滤。

## 限制

- **by_id 只支持单主键**：复合主键实体的 by_id 不会被生成
- **by_filter 是精确匹配**：不支持 LIKE、范围查询等，仅支持字段值精确匹配
- **需要 session_factory**：AutoQueryConfig 需要自己的 session_factory 参数

## 与 @query 共存

自动查询和手动 `@query` / `@mutation` 可以共存：

```python
class Post(SQLModel, table=True):
    # ... 字段定义 ...

    @query
    async def get_recent(cls, days: int = 7) -> list['Post']:
        """自定义查询——自动查询之外"""
        ...

handler = GraphQLHandler(
    base=SQLModel,
    session_factory=async_session,
    auto_query_config=AutoQueryConfig(session_factory=async_session),
)
```

此时 GraphQL schema 同时包含：
- `postById`、`postByFilter`（自动生成）
- `postGetRecent`（手动定义）

## 下一步

- [Core API 模式](./core_api.zh.md) — REST 端点的声明式 DTO 构建
- [GraphQL 模式](./graphql_mode.zh.md) — 完整的 GraphQL 能力
