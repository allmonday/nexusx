# Core API 模式

Core API 模式用于 GraphQL 之外的场景——FastAPI REST 端点、服务层响应组装，或任何用例 DTO。同样的 DataLoader 批量加载，同样的 N+1 预防。

核心概念按顺序递进：**隐式自动加载 → resolve_\* → post_\* → 跨层数据流**。

## Step 1: DefineSubset + 隐式自动加载

最简单的 Core API 用法：从 SQLModel 实体选择字段，声明关系字段——它们自动加载。

```python
from sqlmodel import SQLModel, select
from sqlmodel_nexus import DefineSubset, ErManager

class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None   # 名称匹配 Task.owner 关系 → 自动加载

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    tasks: list[TaskDTO] = []      # 名称匹配 Sprint.tasks 关系 → 自动加载
```

## ErManager 初始化

```python
# 应用启动时——执行一次
er = ErManager(base=SQLModel, session_factory=async_session)
Resolver = er.create_resolver()
```

- `ErManager` 发现所有 SQLModel 实体及其 ORM 关系
- `create_resolver()` 返回一个绑定了实体图的 Resolver 类

**注意**：`base` 和 `entities` 参数互斥——不能同时传两个。

## 在 FastAPI 中使用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/sprints")
async def get_sprints():
    async with async_session() as session:
        sprints = (await session.exec(select(Sprint))).all()
    dtos = [SprintDTO(id=s.id, name=s.name) for s in sprints]
    return await Resolver().resolve(dtos)
```

## 隐式自动加载的四个条件

当以下条件全部满足时，Resolver 自动加载关系字段（无需手写 `resolve_*`）：

1. 字段没有对应的 `resolve_*` 方法
2. 字段是额外字段（不在 `__subset__` 定义中）
3. 字段名匹配已注册的 ORM/自定义关系
4. 字段类型是 BaseModel DTO 且与关系目标实体兼容

## DefineSubset 规则

- `__subset__` 接受元组 `(Entity, ('field1', 'field2'))`
- FK 字段（如 `owner_id`）自动从序列化输出中隐藏，但内部仍可在 `resolve_*` 中访问
- 关系字段声明在类体中（非 `__subset__`），类型必须是 DTO 类型

## 工作原理

```
SprintDTO(id=1, name="Sprint 1")
  → 隐式自动加载: tasks → [TaskDTO(...), TaskDTO(...)]
    → 每个 TaskDTO: 隐式自动加载: owner → UserDTO(...)
  → 结果：完整的嵌套响应树
```

每个关系只执行一次 DataLoader 查询，无论有多少个 Sprint 或 Task。

## DTO 类型约束

```python
# 错误 —— 禁止直接使用 SQLModel 实体
class TaskDTO(DefineSubset):
    owner: User | None = None  # TypeError!

# 正确 —— 使用 DTO 类型
class TaskDTO(DefineSubset):
    owner: UserDTO | None = None  # OK
```

## 下一步

- [Core API 进阶](./core_api_advanced.zh.md) — resolve_*/post_*/跨层数据流
- [自定义关系](./custom_relationship.zh.md) — 非 ORM 关系声明
