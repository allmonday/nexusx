---
name: sqlmodel-nexus-4phase
description: 基于 sqlmodel-nexus 的四阶段开发模式，从 Schema 建模到 API 响应组装再到 TS SDK 的完整项目构建流程。
argument-hint: "[项目路径] 创建四阶段项目的目标目录"
---

# sqlmodel-nexus 四阶段开发模式

基于 sqlmodel-nexus 的渐进式开发方法论。项目在一个 `src/` 目录下逐步演进，每个阶段在上一阶段基础上新增代码。

| Phase | 职责 | 产出 |
|-------|------|------|
| **Phase 1** | Schema + ER Diagram + 聚合根入口 + mock seed | models + db(engine + session) + database(seed) + voyager |
| **Phase 2** | Loader 实现 | models 方法体实现，GraphQL 可查询 |
| **Phase 3** | UseCase 响应组装 + MCP | dtos + services + REST + MCP + Voyager 补充 services |
| **Phase 4** | OpenAPI spec → TS SDK | 端到端 SDK |

## 核心原则

- 优先讨论清楚需求，确认术语定义和实体关系
- 非功能模块与业务模块解耦，业务概念不侵入基础设施层
- **每个阶段必须暂停，展示产出物，等用户确认后再进入下一阶段**
- Phase 间递进：同一项目目录下逐步丰富，只新增不修改已有代码

## 参考实现

读取本 skill 目录下 `template/` 中的代码作为生成参考。严格遵守 template 中的文件结构、import 风格和命名约定。

## 项目结构

单项目渐进演进，每个 Phase 在上一阶段基础上新增文件：

```
src/
├── models.py       # Phase 1 骨架 → Phase 2 补充实现
├── db.py           # Phase 1（engine + session factory，不依赖 models）
├── database.py     # Phase 1（mock seed，依赖 db + models）
├── service/        # Phase 3 新增（每个业务实体一个子目录）
│   ├── task/
│   │   ├── spec.md     # 服务目的、用途、需求、变更记录
│   │   ├── dtos.py     # TaskSummary, UserSummary
│   │   └── service.py  # TaskService
│   └── sprint/
│       ├── spec.md     # 服务目的、用途、需求、变更记录
│       ├── dtos.py     # SprintSummary
│       └── service.py  # SprintService
├── main.py         # 逐步扩展（voyager → graphql → rest → mcp）
└── router/         # Phase 3 新增（可选，按需拆分）
```

## 四阶段定义

### Phase 1: Schema + ER Diagram + 聚合根入口

**目标**: 定义实体、关系、查询/变更契约，用 ER diagram 可视化供团队讨论。

**新增/修改文件**:
- `db.py` — aiosqlite engine + session_factory（不导入 models，避免循环依赖）
- `models.py` — SQLModel 实体 + Relationship + `@query`/`@mutation`（从 `db.py` 导入 `async_session`）
- `database.py` — mock seed data（从 `db.py` 导入 engine/session，从 `models.py` 导入实体）
- `main.py` — FastAPI + Voyager（ER diagram 可视化）+ GraphiQL

**关键模式**:
- SQLModel 实体 + Relationship 声明关系方向
- 每个 Model 必须有 docstring 说明业务含义，每个 Field 必须有 `description` 说明字段语义
- `@query` / `@mutation` 方法体用 `pass` + docstring 描述业务意图
- mock seed data 用于讨论数据样本是否合理（数量、关联关系、边界值）
- Voyager 通过 `create_use_case_voyager(services=[], er_manager=er)` 展示 ER diagram

**阶段结束 → 暂停确认**:
- 展示实体、关系、聚合根划分
- **展示 mock seed data，与用户确认数据样本的合理性和覆盖度**
- 启动服务，Voyager 中查看 ER diagram
- 展示 `/schema` 的 GraphQL SDL
- 等用户全部确认后再进入 Phase 2

### Phase 2: Database + Loader 实现

**目标**: 接入数据库，实现数据获取。ORM 关系通过 DataLoader 自动加载，自定义关系用手写 batch loader。

**新增/修改文件**:
- `models.py` — 方法体从 `pass` 补充为完整 SQLAlchemy async 实现
- `main.py` — GraphQLHandler 接入 session_factory（已有 database.py 和 seed data）

**关键模式**:
- `GraphQLHandler(session_factory=...)` 接入数据库，关系通过 DataLoader 自动批量加载
- `AutoQueryConfig` 自动生成 by_id / by_filter 查询
- 自定义关系用 `__relationships__` + 手写 async batch loader
- Seed data 用于开发测试

**阶段结束 → 暂停确认**:
- 启动服务，在 GraphiQL 中执行查询，验证关系加载正确
- 确认 seed 数据合理、Loader 行为符合预期

### Phase 3: UseCase 响应组装 + MCP

**目标**: 按 API 用例组装响应结构。DefineSubset 隐藏内部字段，UseCaseService 统一业务入口。

**新增/修改文件**:
- `service/<entity>/spec.md` — 服务目的、用途、需求、变更记录
- `service/<entity>/dtos.py` — DefineSubset DTOs
- `service/<entity>/service.py` — UseCaseService
- `router/` — FastAPI REST 端点（调用 Service）
- `main.py` — 挂载 REST router + MCP + Voyager 补充 services

**关键模式**:
- `DefineSubset` + `SubsetConfig` 定义响应 DTO（字段选择、FK 隐藏）
- `ErManager` + `Resolver` 自动加载关系（implicit auto-load）
- `UseCaseService` 统一业务逻辑入口（同时服务 MCP 和 FastAPI）
- `@query` / `@mutation` 装饰器标记服务方法
- `build_dto_select()` 只查 DTO 需要的列
- `create_use_case_voyager()` 可视化服务结构
- `create_use_case_mcp_server()` + `UseCaseAppConfig` 暴露给 AI agent
- REST 端点通过 `tags=[Service.get_tag_name()]` 分组

**阶段结束 → 暂停确认**:
- 启动服务，测试 REST 端点返回数据正确
- 访问 Voyager 确认服务可视化完整
- 测试 MCP 端点可被发现和调用

### Phase 4: OpenAPI → TS SDK

**目标**: 从 FastAPI OpenAPI spec 生成 TypeScript SDK。

提示用户执行：
```bash
npx openapi-typescript http://localhost:8000/openapi.json -o sdk/schema.d.ts
```

**阶段结束 → 暂停确认**:
- 验证生成的 TS 类型与实际 API 一致

## 阶段间变化对照

| 方面 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|
| 实体 | SQLModel 骨架 + docstring + mock seed | 方法体实现 | 继承 Phase 2 | - |
| 关系 | Relationship 声明 | DataLoader 实现 | DefineSubset 隐藏 FK | - |
| 查询 | pass 占位 | SQLAlchemy async | UseCaseService 封装 | - |
| API | Voyager(ER diagram) + GraphiQL | GraphQL | GraphQL + REST + Voyager(+services) + MCP | TS SDK |
| 响应 | N/A | 完整实体 | DefineSubset DTO | OpenAPI spec |

## 踩坑经验

1. **engine/session 必须独立为 `db.py`** — `models.py` 需要 `async_session`，`database.py` 需要 models，放在同一文件会导致循环导入。`db.py` 只放 engine + session_factory，不导入任何 model
2. **`pyproject.toml` 必须配置 `packages = ["src"]`** — hatchling 默认按项目名找目录，`src/` 布局需要显式指定 `[tool.hatch.build.targets.wheel]`
3. **不要在 DefineSubset 文件中使用 `from __future__ import annotations`** — 会使类型注解变字符串，SubsetMeta 无法检测 Annotated 元数据
4. **DTO 字段类型必须用 DTO 类型** — 不能直接用 SQLModel 实体，否则 TypeError
5. **列表关系需要 order_by** — 分页功能要求 `sa_relationship_kwargs={"order_by": "Entity.column"}`
6. **ErManager base 和 entities 互斥** — 不能同时提供
7. **目录命名不能以数字开头** — Python 模块名限制
8. **UseCaseService 只有被 @query/@mutation 装饰的 async classmethod 会被发现** — 普通方法不会暴露
9. **build_dto_select → dict(row._mapping) → DTO 构造** — 这是 Core API 的标准查询模式
10. **每个 Model 必须有 docstring，每个 Field 必须有 description** — Phase 1 就要确保语义清晰，description 会传递到 OpenAPI spec
11. **每个 service 子目录必须包含 spec.md** — 记录服务目的、用途、方法需求、DTO 说明和变更记录，方便团队理解服务边界

## 执行步骤

当用户要求创建四阶段项目时：

1. **确认需求**: 讨论业务领域、实体、关系、聚合根、用例
2. **创建项目结构**: 目录 + pyproject.toml（依赖 sqlmodel-nexus）
3. **Phase 1**: 生成 db.py + models.py + database.py(mock seed) + main.py(voyager) → 展示 ER diagram + SDL + seed data → **暂停等用户确认**
4. **Phase 2**: 补充 models 方法体 → 启动服务 → GraphiQL 查询验证 → **暂停等用户确认**
5. **Phase 3**: 新增 dtos.py + services.py + router → 启动服务 → 测试 REST + Voyager + MCP → **暂停等用户确认**
6. **Phase 4**: 提示 openapi-typescript 命令和 SDK 使用模式 → **暂停等用户确认**
