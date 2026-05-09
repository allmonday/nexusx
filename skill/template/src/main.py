"""FastAPI application entry point.

Phase 1: Voyager (ER diagram) + GraphiQL
Phase 2: + GraphQL with database + seed data
Phase 3: + REST + MCP + Voyager with services
"""
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from src.database import async_session, init_db
from src.models import BaseEntity
from sqlmodel_nexus import GraphQLHandler

# ── GraphQL handler ───────────────────────────────────────────────────

graphql_handler = GraphQLHandler(
    base=BaseEntity,
    session_factory=async_session,
)


# ── FastAPI app ───────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="sqlmodel-nexus Template",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Voyager visualization (Phase 1: ER diagram only) ──────────────────

from sqlmodel_nexus import create_use_case_voyager  # noqa: E402
from src.models import er  # noqa: E402

voyager_app = create_use_case_voyager(
    services=[],  # Phase 3: add UseCaseService classes here
    er_manager=er,
    name="Template API",
)
app.mount("/voyager", voyager_app)


# ── GraphQL endpoints (Phase 2+) ─────────────────────────────────────


class GraphQLRequest(BaseModel):
    query: str
    variables: Optional[dict[str, Any]] = None
    operation_name: Optional[str] = None


@app.get("/graphql", response_class=HTMLResponse)
async def graphiql():
    return graphql_handler.get_graphiql_html()


@app.post("/graphql")
async def graphql_endpoint(req: GraphQLRequest):
    return await graphql_handler.execute(
        query=req.query,
        variables=req.variables,
        operation_name=req.operation_name,
    )


@app.get("/schema", response_class=PlainTextResponse)
async def graphql_schema():
    return graphql_handler.get_sdl()


# ── REST router (Phase 3) ────────────────────────────────────────────

from src.router import api as api_router  # noqa: E402

app.include_router(api_router.route)


# ── MCP — entity-level CRUD (Phase 3) ────────────────────────────────

from sqlmodel_nexus.mcp import create_mcp_server  # noqa: E402

mcp = create_mcp_server(
    apps=[{
        "name": "template",
        "base": BaseEntity,
        "session_factory": async_session,
        "description": "Template entities CRUD.",
    }],
    name="Template MCP Server",
    allow_mutation=True,
)
app.mount("/mcp", mcp.http_app(path="/"))


# ── MCP — UseCase business methods (Phase 3) ─────────────────────────

from sqlmodel_nexus import UseCaseAppConfig, create_use_case_mcp_server  # noqa: E402
from src.service.sprint.service import SprintService  # noqa: E402
from src.service.task.service import TaskService  # noqa: E402

use_case_mcp = create_use_case_mcp_server(
    apps=[
        UseCaseAppConfig(
            name="template",
            services=[TaskService, SprintService],
            description="Task & Sprint business services",
        ),
    ],
    name="Template UseCase MCP",
)
app.mount("/mcp-usecase", use_case_mcp.http_app(path="/"))
