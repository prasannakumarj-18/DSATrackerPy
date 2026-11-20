"""SQLite storage + all progress calculations (no UI code here)."""
import os
import sqlite3
import time
from datetime import date, datetime

from roadmap_data import SECTIONS, all_topics

NOT_STARTED, IN_PROGRESS, COMPLETED = 0, 1, 2
STATUS_LABELS = {NOT_STARTED: "Not Started", IN_PROGRESS: "In Progress", COMPLETED: "Completed"}
LOW, MEDIUM, HIGH = 0, 1, 2
PRIORITY_LABELS = {LOW: "Low", MEDIUM: "Medium", HIGH: "High"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    group_name TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    completed_at INTEGER,
    UNIQUE (section_id, group_name, title)
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 1,
    due_day INTEGER NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at INTEGER,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS daily_activity (
    day INTEGER PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL,
    goal TEXT NOT NULL,
    language TEXT NOT NULL,
    daily_target INTEGER NOT NULL
);
"""


def today() -> int:
    """Days are stored as date.toordinal() integers."""
    return date.today().toordinal()


def day_of(millis: int) -> int:
    return datetime.fromtimestamp(millis / 1000).date().toordinal()


def format_day(day: int) -> str:
    return date.fromordinal(day).strftime("%d %b %Y")


def format_millis(millis: int) -> str:
    return format_day(day_of(millis))


def default_db_path() -> str:
    # On Android/iOS Flet sets FLET_APP_STORAGE_DATA to a writable, persistent folder.
    folder = os.getenv("FLET_APP_STORAGE_DATA") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "storage"
    )
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "dsa_tracker.db")


def compute_streak(active_days: set, today_day: int) -> int:
    if today_day in active_days:
        day = today_day
    elif today_day - 1 in active_days:
        day = today_day - 1
    else:
        return 0
    streak = 0
    while day in active_days:
        streak += 1
        day -= 1
    return streak


class Database:
    def __init__(self, path: str = None):
        self.path = path or default_db_path()
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.seed()

    # ---------- setup ----------
    def seed(self):
        """Safe to run on every launch: the UNIQUE constraint blocks duplicates."""
        self.conn.executemany(
            "INSERT OR IGNORE INTO topics (section_id, group_name, title, order_index) "
            "VALUES (?, ?, ?, ?)",
            all_topics(),
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO profile (id, username, goal, language, daily_target) "
            "VALUES (1, 'Sai', 'Master Data Structures & Algorithms', 'Python', 60)"
        )
        self.conn.commit()

    # ---------- topics ----------
    def topics(self, section_id: int = None) -> list:
        if section_id is None:
            rows = self.conn.execute(
                "SELECT * FROM topics ORDER BY section_id, order_index").fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM topics WHERE section_id = ? ORDER BY order_index",
                (section_id,)).fetchall()
        return [dict(r) for r in rows]

    def set_topic_status(self, topic_id: int, new_status: int):
        row = self.conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
        if row is None or row["status"] == new_status:
            return
        was_done = row["status"] == COMPLETED
        now_done = new_status == COMPLETED
        completed_at = int(time.time() * 1000) if now_done else None
        self.conn.execute("UPDATE topics SET status = ?, completed_at = ? WHERE id = ?",
                          (new_status, completed_at, topic_id))
        if now_done:
            self._bump(today(), +1)
        elif was_done and row["completed_at"]:
            self._bump(day_of(row["completed_at"]), -1)
        self.conn.commit()

    def save_topic_notes(self, topic_id: int, notes: str):
        self.conn.execute("UPDATE topics SET notes = ? WHERE id = ?", (notes.strip(), topic_id))
        self.conn.commit()

    # ---------- tasks ----------
    def tasks(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM tasks ORDER BY completed ASC, due_day ASC, priority DESC, id ASC"
        ).fetchall()
        return [dict(r) for r in rows]

    def add_task(self, title: str, priority: int, due_day: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO tasks (title, priority, due_day, created_at) VALUES (?, ?, ?, ?)",
            (title.strip(), priority, due_day, int(time.time() * 1000)))
        self.conn.commit()
        return cur.lastrowid

    def update_task(self, task_id: int, title: str, priority: int, due_day: int):
        self.conn.execute("UPDATE tasks SET title = ?, priority = ?, due_day = ? WHERE id = ?",
                          (title.strip(), priority, due_day, task_id))
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def set_task_completed(self, task_id: int, completed: bool):
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None or bool(row["completed"]) == completed:
            return
        completed_at = int(time.time() * 1000) if completed else None
        self.conn.execute("UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?",
                          (1 if completed else 0, completed_at, task_id))
        if completed:
            self._bump(today(), +1)
        elif row["completed_at"]:
            self._bump(day_of(row["completed_at"]), -1)
        self.conn.commit()

    # ---------- profile ----------
    def profile(self) -> dict:
        return dict(self.conn.execute("SELECT * FROM profile WHERE id = 1").fetchone())

    def save_profile(self, username: str, goal: str, language: str, daily_target: int):
        self.conn.execute(
            "UPDATE profile SET username = ?, goal = ?, language = ?, daily_target = ? WHERE id = 1",
            (username.strip() or "Sai", goal.strip(), language, int(daily_target)))
        self.conn.commit()

    def reset_progress(self):
        """Clears topic status/notes/dates and activity history. Tasks are kept."""
        self.conn.execute("UPDATE topics SET status = 0, notes = '', completed_at = NULL")
        self.conn.execute("DELETE FROM daily_activity")
        self.conn.commit()

    # ---------- activity / stats ----------
    def _bump(self, day: int, delta: int):
        self.conn.execute("INSERT OR IGNORE INTO daily_activity (day, count) VALUES (?, 0)", (day,))
        self.conn.execute("UPDATE daily_activity SET count = MAX(0, count + ?) WHERE day = ?",
                          (delta, day))

    def stats(self) -> dict:
        topics = self.topics()
        tasks = self.tasks()
        activity = {r["day"]: r["count"] for r in
                    self.conn.execute("SELECT day, count FROM daily_activity").fetchall()}
        active_days = {d for d, c in activity.items() if c > 0}
        t = today()

        sections = []
        for sid, title, _sub in SECTIONS:
            inside = [x for x in topics if x["section_id"] == sid]
            sections.append({
                "id": sid, "title": title, "total": len(inside),
                "completed": sum(1 for x in inside if x["status"] == COMPLETED),
            })

        weekly = []
        for offset in range(6, -1, -1):
            d = t - offset
            weekly.append({
                "label": date.fromordinal(d).strftime("%a"),
                "count": activity.get(d, 0),
                "is_today": offset == 0,
            })

        next_topic = next((x for x in topics if x["status"] == IN_PROGRESS), None) \
            or next((x for x in topics if x["status"] == NOT_STARTED), None)

        recent = sorted((x for x in topics if x["status"] == COMPLETED),
                        key=lambda x: x["completed_at"] or 0, reverse=True)[:5]

        total = len(topics)
        completed = sum(1 for x in topics if x["status"] == COMPLETED)
        return {
            "total": total,
            "completed": completed,
            "in_progress": sum(1 for x in topics if x["status"] == IN_PROGRESS),
            "not_started": sum(1 for x in topics if x["status"] == NOT_STARTED),
            "fraction": (completed / total) if total else 0.0,
            "tasks_completed": sum(1 for x in tasks if x["completed"]),
            "tasks_pending": sum(1 for x in tasks if not x["completed"]),
            "today_tasks": sorted((x for x in tasks if x["due_day"] == t),
                                  key=lambda x: x["completed"]),
            "streak": compute_streak(active_days, t),
            "learning_days": len(active_days),
            "sections": sections,
            "weekly": weekly,
            "next_topic": next_topic,
            "recent": recent,
            "profile": self.profile(),
        }
