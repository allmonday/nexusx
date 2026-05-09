# 自定义关系

对于不存在于 ORM 中的关系——跨服务调用、计算边、非数据库来源——使用 `Relationship` 在实体上声明。

## 为什么需要自定义关系

标准场景下，SQLModel 的 `Relationship` 和 `Field(foreign_key=...)` 已经覆盖了数据库内的关系。但以下场景需要自定义：

- **跨服务调用**：从外部 API 加载关联数据
- **计算边**：基于业务逻辑而非 FK 的关联
- **非数据库来源**：缓存、搜索引擎、文件系统

## 声明方式

在 SQLModel 实体的 `__relationships__` 列表中声明：

```python
from sqlmodel_nexus import Relationship

async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    """批量加载 tags。"""
    async with get_session() as session:
        stmt = (
            select(Tag, TaskTag.task_id)
            .join(TaskTag)
            .where(TaskTag.task_id.in_(task_ids))
        )
        rows = (await session.exec(stmt)).all()
        return build_list(rows, task_ids, lambda row: row[1], lambda row: row[0])

class Task(SQLModel, table=True):
    __relationships__ = [
        Relationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
    ]
    id: int | None = Field(default=None, primary_key=True)
    title: str
```

## Relationship 参数详解

| 参数 | 类型 | 说明 |
|------|------|------|
| `fk` | `str` | 源实体上用于 DataLoader 收集键值的字段名 |
| `target` | `type` | 目标类型（`Entity` 或 `list[Entity]`） |
| `name` | `str` | 关系名称，用于隐式自动加载时的字段匹配 |
| `loader` | `type` or `callable` | DataLoader 类或异步批量函数 |

### target 语法

```python
# 单个目标
Relationship(fk="owner_id", target=User, name="owner", loader=user_loader)

# 列表目标
Relationship(fk="id", target=list[Tag], name="tags", loader=tags_loader)
```

## 与隐式自动加载配合

自定义关系与 ORM 关系使用相同的自动加载机制：

```python
class TagDTO(DefineSubset):
    __subset__ = (Tag, ("id", "name"))

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title"))
    tags: list[TagDTO] = []   # 名称 "tags" 匹配自定义关系 → 自动加载
```

只要满足隐式自动加载的四个条件，自定义关系也会被自动处理。

## DataLoader 批量函数

`loader` 可以是 DataLoader 类或异步批量函数。批量函数接收一个键值列表，返回对应的结果：

```python
# 单个目标（fk → 单个实体）
async def user_loader(user_ids: list[int]) -> dict[int, User]:
    users = await fetch_users(user_ids)
    return {u.id: u for u in users}

# 列表目标（fk → 实体列表）
async def tags_loader(task_ids: list[int]) -> list[list[Tag]]:
    tags = await fetch_tags_for_tasks(task_ids)
    return group_by_task(tags, task_ids)
```

## 下一步

- [ER 图](./er_diagram.zh.md) — 实体关系的可视化
- [Core API 模式](./core_api.zh.md) — 在 DTO 中使用自定义关系
