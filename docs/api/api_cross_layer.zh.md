# 跨层数据流 API

ExposeAs、SendTo、Collector 的完整 API 参考。

## ExposeAs

将祖先字段暴露给后代节点，通过 `ancestor_context` 访问。

```python
from typing import Annotated
from nexusx import ExposeAs

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    name: Annotated[str, ExposeAs('sprint_name')]
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `key` | `str` | 在 `ancestor_context` 中的键名 |

### 在后代中访问

```python
class TaskDTO(DefineSubset):
    def post_full_title(self, ancestor_context):
        return f"{ancestor_context['sprint_name']} / {self.title}"
```

`ancestor_context` 是一个 `dict`，收集了所有祖先节点通过 `ExposeAs` 暴露的值。

## SendTo

将后代字段值发送到祖先的 Collector。

```python
from typing import Annotated
from nexusx import SendTo

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: Annotated[UserDTO | None, SendTo('contributors')] = None
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `collector_name` | `str` | 目标 Collector 的名称 |

## Collector

在 `post_*` 方法中接收后代通过 `SendTo` 发送的值。

```python
from nexusx import Collector

class SprintDTO(DefineSubset):
    contributors: list[UserDTO] = []

    def post_contributors(self, collector=Collector('contributors')):
        return collector.values()
```

### Collector 方法

| 方法 | 说明 |
|------|------|
| `values()` | 返回所有收集到的值列表 |

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | Collector 名称，匹配 `SendTo` 的目标名 |
