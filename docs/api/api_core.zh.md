# Core API 参考

ErManager、Resolver、DefineSubset、Loader 的完整 API 参考。

## ErManager

实体关系管理器——发现实体、注册关系、创建 Resolver。

```python
from sqlmodel_nexus import ErManager

er = ErManager(
    base=SQLModel,                    # SQLModel 基类（与 entities 互斥）
    entities=None,                    # 显式实体列表（与 base 互斥）
    session_factory=async_session,    # 异步 session 工厂
)
```

**注意**：`base` 和 `entities` 互斥，不能同时传。

### 方法

| 方法 | 说明 |
|------|------|
| `create_resolver()` | 返回绑定了实体图的 Resolver 类 |
| `get_diagram()` | 返回 ErDiagram 实例 |

## Resolver

由 `ErManager.create_resolver()` 返回的类。用于解析 DTO 树。

```python
Resolver = er.create_resolver()

result = await Resolver().resolve(dtos)
```

### Resolver 构造器参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `context` | `dict` | 全局上下文，可通过 `ancestor_context` 访问 |
| `loader_params` | `dict` | DataLoader 额外参数 |
| `debug` | `bool` | 启用调试日志 |

### Resolver.resolve

```python
result = await Resolver().resolve(dtos)
```

参数 `dtos` 可以是单个 DTO 实例或 DTO 列表。返回解析后的同一对象（就地修改）。

### 执行顺序

1. 执行所有 `resolve_*` 方法（加载关系数据）
2. 遍历已有的对象字段
3. 执行所有 `post_*` 方法（计算派生字段）
4. 收集 SendTo 值到祖先的 Collector

## DefineSubset

DTO 基类——从 SQLModel 实体生成 Pydantic 模型。

```python
from sqlmodel_nexus import DefineSubset

class UserDTO(DefineSubset):
    __subset__ = (User, ("id", "name"))
```

### __subset__ 语法

接受元组 `(Entity, ('field1', 'field2'))` 或 `SubsetConfig` 对象。

### 规则

- FK 字段自动从序列化输出隐藏（`exclude=True`），但内部仍可用
- 关系字段声明在类体中（非 `__subset__`），类型必须是 DTO 类型
- 禁止直接使用 SQLModel 实体作为字段类型

## SubsetConfig

声明式 DTO 配置（`__subset__` 的替代形式）：

```python
from sqlmodel_nexus import SubsetConfig

class UserDTO(DefineSubset):
    __subset__ = SubsetConfig(entity=User, fields=("id", "name"))
```

## Loader

在 `resolve_*` 方法中声明 DataLoader 依赖。

```python
from sqlmodel_nexus import Loader

# DataLoader 类
def resolve_tags(self, loader=Loader(TagLoader)):
    return loader.load(self.id)

# 异步批量函数
async def load_users(user_ids):
    ...
def resolve_owner(self, loader=Loader(load_users)):
    return loader.load(self.owner_id)
```

**Loader 依赖名必须匹配关系名**：`Loader('author')` 要求 ErManager 中有名为 `author` 的关系。

## build_dto_select

辅助函数，构建从 SQL 数据库查询 DTO 所需字段的 SELECT 语句：

```python
from sqlmodel_nexus import build_dto_select

stmt = build_dto_select(SprintSummary)
stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
```
