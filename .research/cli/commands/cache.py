"""Cache commands: cache stats, cache clear."""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def cmd_cache(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    cache_dir = root / ".research" / "cache"
    db_path = cache_dir / "research_cache.db"

    if args.action == "stats":
        print("=" * 60)
        print("CACHE STATISTICS")
        print("=" * 60)
        print()

        total_size = 0
        file_count = 0
        for f in cache_dir.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size
                file_count += 1

        print(f"  Cache directory: {cache_dir}")
        print(f"  Total size: {total_size / 1024:.1f} KB")
        print(f"  Files: {file_count}")
        print()

        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                print(f"  Database: {db_path.name}")
                print(f"  Tables: {', '.join(tables)}")
                print()

                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    try:
                        cursor.execute(f"SELECT MAX(timestamp) FROM {table}")
                        latest = cursor.fetchone()[0]
                    except Exception:
                        latest = None
                    print(f"    {table}: {count} entries (latest: {latest or 'N/A'})")

                conn.close()
            except Exception as e:
                print(f"  ERROR reading database: {e}")
        else:
            print("  Database not found.")

        print()

        index_path = cache_dir / "skill_index.json"
        if index_path.exists():
            index_data = load_json(index_path)
            skill_count = len(index_data.get("skills", []))
            index_size = index_path.stat().st_size
            print(f"  Skill index: {skill_count} skills ({index_size / 1024:.1f} KB)")
        print()

    elif args.action == "clear":
        older_than = args.older_than or "7d"
        print(f"Clearing cache entries older than {older_than}...")

        if db_path.exists():
            try:
                import sqlite3
                days = 7
                if older_than.endswith("d"):
                    days = int(older_than[:-1])
                elif older_than.endswith("h"):
                    days = int(older_than[:-1]) / 24

                cutoff = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff.isoformat()

                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                total_deleted = 0
                for table in tables:
                    cursor.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_str,))
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    if deleted > 0:
                        print(f"  Deleted {deleted} entries from {table}")

                conn.commit()
                conn.close()

                conn = sqlite3.connect(str(db_path))
                conn.execute("VACUUM")
                conn.close()

                print(f"  Total deleted: {total_deleted} entries")
            except Exception as e:
                print(f"  ERROR clearing cache: {e}")
        else:
            print("  No cache database found.")

        print()
