"""Profile nexusx Resolver traversal with cProfile.

Focuses on L3 (SprintSummary) at Medium scale (200 tasks) — the most representative
scenario. Runs the nexusx path only, outputs top functions by cumulative time.

Usage:
    uv run python benchmarks/profile_resolver.py                  # SQLite
    uv run python benchmarks/profile_resolver.py --mysql          # MySQL
"""

import asyncio
import cProfile
import pstats
import sys
from pathlib import Path

# Add project root to path so benchmarks module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.bench_resolver import (
    USE_MYSQL,
    SprintSummary,
    _ensure_engine,
    _ensure_resolver,
    bench_nexusx_l3,
    setup_db,
    seed_data,
)

N_WARMUP = 5
N_PROFILE_RUNS = 20


async def profile_l3():
    db_label = "MySQL 8.0 (localhost)" if USE_MYSQL else "SQLite in-memory"
    print(f"Profiling nexusx L3 (SprintSummary) — {db_label}, Medium scale (200 tasks)")
    print()

    await setup_db()
    await seed_data(20, 10, 20)
    _ensure_resolver()

    # Warmup
    for _ in range(N_WARMUP):
        await bench_nexusx_l3()

    # Profile
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(N_PROFILE_RUNS):
        await bench_nexusx_l3()
    profiler.disable()

    # Print results — sorted by cumulative time, filtered to nexusx code
    stats = pstats.Stats(profiler)

    print("=" * 80)
    print("  Top 40 by cumulative time (nexusx code only)")
    print("=" * 80)
    stats.sort_stats("cumulative")
    stats.print_stats("nexusx", 40)

    print()
    print("=" * 80)
    print("  Top 30 by total time (all calls)")
    print("=" * 80)
    stats.sort_stats("time")
    stats.print_stats(30)

    print()
    print("=" * 80)
    print("  Resolver._traverse callees")
    print("=" * 80)
    stats.sort_stats("cumulative")
    stats.print_stats("_traverse", 20)

    print()
    print("=" * 80)
    print("  _scan_auto_load_fields detail")
    print("=" * 80)
    stats.sort_stats("cumulative")
    stats.print_stats("_scan_auto_load|_extract_dto|_get_object_fields|_get_class_meta", 20)

    print()
    print("=" * 80)
    print("  ContextVar overhead")
    print("=" * 80)
    stats.sort_stats("cumulative")
    stats.print_stats("ContextVar|contextvars|_prepare_expose|_prepare_collectors", 20)


if __name__ == "__main__":
    asyncio.run(profile_l3())
