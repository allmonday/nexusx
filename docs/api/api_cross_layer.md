# Cross-layer Data Flow API

Complete API reference for ExposeAs, SendTo, and Collector.

## ExposeAs

Exposes ancestor fields to descendant nodes, accessible via `ancestor_context`.

```python
from typing import Annotated
from nexusx import ExposeAs

class SprintDTO(DefineSubset):
    __subset__ = (Sprint, ("id", "name"))
    name: Annotated[str, ExposeAs('sprint_name')]
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | Key name in `ancestor_context` |

### Accessing in Descendants

```python
class TaskDTO(DefineSubset):
    def post_full_title(self, ancestor_context):
        return f"{ancestor_context['sprint_name']} / {self.title}"
```

`ancestor_context` is a `dict` collecting all values exposed by ancestors through `ExposeAs`.

## SendTo

Sends descendant field values to an ancestor's Collector.

```python
from typing import Annotated
from nexusx import SendTo

class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: Annotated[UserDTO | None, SendTo('contributors')] = None
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `collector_name` | `str` | Name of the target Collector |

## Collector

Receives values sent by descendants via `SendTo` in `post_*` methods.

```python
from nexusx import Collector

class SprintDTO(DefineSubset):
    contributors: list[UserDTO] = []

    def post_contributors(self, collector=Collector('contributors')):
        return collector.values()
```

### Collector Methods

| Method | Description |
|--------|-------------|
| `values()` | Returns a list of all collected values |

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Collector name, matching the `SendTo` target name |
