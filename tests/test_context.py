"""Tests for cross-layer data flow: ExposeAs, SendTo, Collector."""

from __future__ import annotations

import pytest
from typing import Annotated

from pydantic import BaseModel

from nexusx.context import Collector, ExposeAs, SendTo
from nexusx.resolver import Resolver

# ──────────────────────────────────────────────────────────
# Test: ExposeAs — ancestor context passing
# ──────────────────────────────────────────────────────────

class TestExposeAs:
    async def test_basic_expose_to_descendant(self):
        """ExposeAs field should be available in descendant ancestor_context."""

        class Child(BaseModel):
            name: str
            parent_greeting: str = ""

            def post_parent_greeting(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                return ancestor_context.get("greeting", "no greeting")

        class Parent(BaseModel):
            greeting: Annotated[str, ExposeAs("greeting")]
            children: list[Child] = []

        parent = Parent(
            greeting="Hello from parent",
            children=[Child(name="A"), Child(name="B")],
        )
        result = await Resolver().resolve(parent)

        assert result.children[0].parent_greeting == "Hello from parent"
        assert result.children[1].parent_greeting == "Hello from parent"

    async def test_multi_level_expose(self):
        """ExposeAs should propagate through multiple levels."""

        class GrandChild(BaseModel):
            name: str
            root_name: str = ""

            def post_root_name(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                return ancestor_context.get("root_name", "unknown")

        class Child(BaseModel):
            name: str
            children: list[GrandChild] = []

        class Root(BaseModel):
            name: Annotated[str, ExposeAs("root_name")]
            children: list[Child] = []

        root = Root(
            name="RootNode",
            children=[
                Child(name="Child1", children=[GrandChild(name="GC1")]),
                Child(name="Child2", children=[GrandChild(name="GC2")]),
            ],
        )
        result = await Resolver().resolve(root)

        assert result.children[0].children[0].root_name == "RootNode"
        assert result.children[1].children[0].root_name == "RootNode"

    async def test_expose_with_resolve(self):
        """ExposeAs should work alongside resolve_* methods."""

        class Child(BaseModel):
            name: str
            full_label: str = ""

            def resolve_name(self):
                return f"child_{self.name}"

            def post_full_label(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                prefix = ancestor_context.get("prefix", "")
                return f"{prefix}/{self.name}"

        class Parent(BaseModel):
            prefix: Annotated[str, ExposeAs("prefix")]
            children: list[Child] = []

        parent = Parent(
            prefix="P",
            children=[Child(name="A"), Child(name="B")],
        )
        result = await Resolver().resolve(parent)

        # resolve_name changes name, post uses it
        assert result.children[0].full_label == "P/child_A"
        assert result.children[1].full_label == "P/child_B"

    async def test_expose_multiple_fields(self):
        """Multiple ExposeAs fields on one node."""

        class Child(BaseModel):
            info: str = ""

            def post_info(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                return f"{ancestor_context.get('a', '')}-{ancestor_context.get('b', '')}"

        class Parent(BaseModel):
            field_a: Annotated[str, ExposeAs("a")]
            field_b: Annotated[str, ExposeAs("b")]
            children: list[Child] = []

        parent = Parent(field_a="A", field_b="B", children=[Child()])
        result = await Resolver().resolve(parent)

        assert result.children[0].info == "A-B"


# ──────────────────────────────────────────────────────────
# Test: SendTo + Collector — upward aggregation
# ──────────────────────────────────────────────────────────

class TestSendToCollector:
    async def test_basic_collector(self):
        """Collector should aggregate values from SendTo-annotated fields."""

        class Child(BaseModel):
            name: Annotated[str, SendTo("names")]

        class Parent(BaseModel):
            children: list[Child] = []
            collected_names: list[str] = []

            def post_collected_names(self, collector=Collector("names")):
                return collector.values()

        parent = Parent(
            children=[Child(name="Alice"), Child(name="Bob"), Child(name="Charlie")]
        )
        result = await Resolver().resolve(parent)

        assert "Alice" in result.collected_names
        assert "Bob" in result.collected_names
        assert "Charlie" in result.collected_names

    async def test_collector_flat_mode(self):
        """Collector with flat=True should flatten list values."""

        class Child(BaseModel):
            tags: Annotated[list[str], SendTo("all_tags")] = []

        class Parent(BaseModel):
            children: list[Child] = []
            all_tags: list[str] = []

            def post_all_tags(self, collector=Collector("all_tags", flat=True)):
                return collector.values()

        parent = Parent(
            children=[
                Child(tags=["a", "b"]),
                Child(tags=["c", "d"]),
            ]
        )
        result = await Resolver().resolve(parent)

        assert result.all_tags == ["a", "b", "c", "d"]

    async def test_collector_with_resolve(self):
        """Collector should work with resolve_* — collected after resolve."""

        class Child(BaseModel):
            name: str = ""
            resolved_name: Annotated[str, SendTo("resolved")] = ""

            def resolve_resolved_name(self):
                return f"resolved_{self.name}"

        class Parent(BaseModel):
            children: list[Child] = []
            resolved_names: list[str] = []

            def post_resolved_names(self, collector=Collector("resolved")):
                return collector.values()

        parent = Parent(
            children=[
                Child(name="Alice"),
                Child(name="Bob"),
            ]
        )
        result = await Resolver().resolve(parent)

        # resolve_resolved_name runs first, sets the field
        # then _add_values_into_collectors reads the resolved value
        assert result.children[0].resolved_name == "resolved_Alice"
        assert "resolved_Alice" in result.resolved_names
        assert "resolved_Bob" in result.resolved_names

    async def test_collector_none_value_skipped(self):
        """SendTo fields with None value should not be collected."""

        class Child(BaseModel):
            name: str
            optional_val: Annotated[str | None, SendTo("vals")] = None

        class Parent(BaseModel):
            children: list[Child] = []
            values: list[str] = []

            def post_values(self, collector=Collector("vals")):
                return collector.values()

        parent = Parent(
            children=[
                Child(name="A", optional_val="yes"),
                Child(name="B"),  # None default
                Child(name="C", optional_val="yes2"),
            ]
        )
        result = await Resolver().resolve(parent)

        assert result.values == ["yes", "yes2"]


# ──────────────────────────────────────────────────────────
# Test: ExposeAs + SendTo + Collector combined
# ──────────────────────────────────────────────────────────

class TestCombinedContext:
    async def test_full_cross_layer_flow(self):
        """Full scenario: parent exposes context → child uses it and sends data back."""

        class TaskItem(BaseModel):
            title: str
            full_title: str = ""
            completed: Annotated[bool, SendTo("completed_tasks")] = False

            def post_full_title(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                sprint_name = ancestor_context.get("sprint_name", "unknown")
                return f"{sprint_name} / {self.title}"

        class SprintItem(BaseModel):
            name: Annotated[str, ExposeAs("sprint_name")]
            tasks: list[TaskItem] = []
            completed_titles: list[str] = []

            def post_completed_titles(self, collector=Collector("completed_tasks")):
                return collector.values()

        sprint = SprintItem(
            name="Sprint 1",
            tasks=[
                TaskItem(title="Task A", completed=True),
                TaskItem(title="Task B", completed=False),
                TaskItem(title="Task C", completed=True),
            ],
        )
        result = await Resolver().resolve(sprint)

        # ExposeAs: children see sprint_name
        assert result.tasks[0].full_title == "Sprint 1 / Task A"
        assert result.tasks[1].full_title == "Sprint 1 / Task B"

        # SendTo + Collector: parent collects completed task values
        assert result.completed_titles == [True, False, True]

    async def test_expose_and_collector_on_resolve_fields(self):
        """ExposeAs and Collector work with DataLoader-resolved fields."""

        class ChildDTO(BaseModel):
            name: str = ""
            label: str = ""

            def resolve_name(self):
                return "resolved_child"

            def post_label(self, ancestor_context=None):
                if ancestor_context is None:
                    ancestor_context = {}
                prefix = ancestor_context.get("prefix", "?")
                return f"{prefix}:{self.name}"

        class ParentDTO(BaseModel):
            prefix: Annotated[str, ExposeAs("prefix")]
            children: list[ChildDTO] = []

        parent = ParentDTO(
            prefix="P",
            children=[ChildDTO(), ChildDTO()],
        )
        result = await Resolver().resolve(parent)

        assert result.children[0].label == "P:resolved_child"
        assert result.children[1].label == "P:resolved_child"


# ──────────────────────────────────────────────────────────
# Test: BFS edge cases — SendTo multi-collector
# ──────────────────────────────────────────────────────────


class TestSendToMultiCollector:
    async def test_send_to_multiple_collectors(self):
        """One field can send to multiple Collectors via SendTo tuple."""

        class Child(BaseModel):
            name: Annotated[str, SendTo(("names", "all_names"))]

        class Parent(BaseModel):
            children: list[Child] = []
            names: list[str] = []
            all_names: list[str] = []

            def post_names(self, collector=Collector("names")):
                return collector.values()

            def post_all_names(self, collector=Collector("all_names")):
                return collector.values()

        parent = Parent(children=[Child(name="Alice"), Child(name="Bob")])
        result = await Resolver().resolve(parent)

        assert "Alice" in result.names
        assert "Bob" in result.names
        assert "Alice" in result.all_names
        assert "Bob" in result.all_names


# ──────────────────────────────────────────────────────────
# Test: Auto-load + SendTo — verify no duplication
# ──────────────────────────────────────────────────────────


class TestAutoLoadSendTo:
    @pytest.mark.usefixtures("test_db")
    async def test_autoload_no_sendto_duplication(self):
        """Auto-loaded children should not be traversed twice (SendTo values)."""
        from sqlmodel import select

        from nexusx.loader.registry import ErManager
        from nexusx.subset import DefineSubset
        from tests.conftest import (
            FixtureSprint,
            FixtureTask,
            FixtureUser,
            get_test_session_factory,
        )

        session_factory = get_test_session_factory()
        registry = ErManager(
            entities=[FixtureUser, FixtureSprint, FixtureTask],
            session_factory=session_factory,
        )

        class UserDTO(DefineSubset):
            __subset__ = (FixtureUser, ("id", "name"))

        class TaskDTO(DefineSubset):
            __subset__ = (FixtureTask, ("id", "title", "owner_id"))
            owner: UserDTO | None = None
            title_value: Annotated[str, SendTo("titles")] = ""

            def post_title_value(self):
                return self.title

        class SprintDTO(DefineSubset):
            __subset__ = (FixtureSprint, ("id", "name"))
            tasks: list[TaskDTO] = []
            titles: list[str] = []

            def post_titles(self, collector=Collector("titles")):
                return collector.values()

        async with session_factory() as session:
            sprints = (await session.exec(select(FixtureSprint))).all()

        dtos = [SprintDTO(id=s.id, name=s.name) for s in sprints]
        result = await Resolver(registry).resolve(dtos)

        # Each sprint has exactly 2 tasks — titles should appear once each
        assert len(result[0].titles) == 2
        assert len(result[1].titles) == 2
