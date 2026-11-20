"""DSA Tracker - Flet UI (Flet 0.28.x). All data logic lives in db.py."""
from datetime import datetime, date

import flet as ft

import db as dbm
from roadmap_data import SECTIONS

# ---------- palette ----------
BG = "#0A0F1F"
SURFACE = "#131A2E"
SURFACE_HI = "#1B2440"
OUTLINE = "#263052"
TRACK = "#232C4A"
TEXT = "#E8ECF8"
DIM = "#9AA4C4"
PURPLE = "#8B5CF6"
BLUE = "#3B82F6"
CYAN = "#22D3EE"
GREEN = "#34D399"
AMBER = "#FBBF24"
RED = "#F87171"

STATUS_COLORS = {dbm.NOT_STARTED: DIM, dbm.IN_PROGRESS: BLUE, dbm.COMPLETED: GREEN}
PRIORITY_COLORS = {dbm.LOW: GREEN, dbm.MEDIUM: AMBER, dbm.HIGH: RED}
LANGUAGES = ["Python", "Java", "C++", "C#", "JavaScript", "Go", "Rust", "Ruby", "Kotlin"]


# ---------- small UI helpers ----------
def card(content, padding=16):
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border=ft.border.all(1, OUTLINE),
        border_radius=20,
        padding=padding,
    )


def title_text(text, size=20):
    return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=TEXT)


def dim_text(text, size=13):
    return ft.Text(text, size=size, color=DIM)


def stat_tile(label, value, color):
    return ft.Container(
        content=ft.Column(
            [ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD, color=color),
             dim_text(label)],
            spacing=2,
        ),
        bgcolor=SURFACE,
        border=ft.border.all(1, OUTLINE),
        border_radius=20,
        padding=16,
        expand=True,
    )


def progress_ring(fraction, size=120):
    return ft.Stack(
        [
            ft.ProgressRing(value=fraction, stroke_width=12, width=size, height=size,
                            color=PURPLE, bgcolor=TRACK),
            ft.Container(
                content=ft.Text(f"{round(fraction * 100)}%", size=22,
                                weight=ft.FontWeight.BOLD, color=TEXT),
                alignment=ft.alignment.center, width=size, height=size),
        ],
        width=size, height=size,
    )


def bar(fraction, color=CYAN, height=8):
    return ft.ProgressBar(value=fraction, color=color, bgcolor=TRACK, bar_height=height)


def empty_state(icon, title, message):
    return ft.Container(
        content=ft.Column(
            [ft.Icon(icon, size=48, color=PURPLE),
             ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT,
                     text_align=ft.TextAlign.CENTER),
             ft.Text(message, size=13, color=DIM, text_align=ft.TextAlign.CENTER)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=24, alignment=ft.alignment.center)


# ---------- app ----------
def main(page: ft.Page):
    database = dbm.Database()

    page.title = "DSA Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=PURPLE)
    page.bgcolor = BG
    page.padding = 0

    state = {
        "tab": 0,
        "task_filter": "today",
        "expanded": set(),
        "roadmap_list": None,
        "roadmap_header": None,
        "focus": None,
    }

    body = ft.Container(expand=True, padding=16)

    def snack(message):
        page.open(ft.SnackBar(ft.Text(message)))

    def confirm(title, message, confirm_label, on_yes):
        def yes(e):
            page.close(dlg)
            on_yes()

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                ft.TextButton(confirm_label, on_click=yes,
                              style=ft.ButtonStyle(color=RED)),
            ],
        )
        page.open(dlg)

    # =====================================================
    # HOME
    # =====================================================
    def build_home():
        s = database.stats()
        nxt = s["next_topic"]

        def go_continue(e):
            sid = nxt["section_id"] if nxt else 1
            state["expanded"].add(sid)
            state["focus"] = sid
            nav.selected_index = 1
            show_tab(1)

        if nxt:
            cont_label = f"Continue Learning: {nxt['title']}"
        elif s["total"]:
            cont_label = "All topics done - review roadmap"
        else:
            cont_label = "Open Roadmap"

        if s["today_tasks"]:
            task_rows = [
                ft.Row([
                    ft.Checkbox(value=bool(t["completed"]),
                                on_change=lambda e, tid=t["id"]: toggle_task_home(tid, e.control.value)),
                    ft.Text(t["title"], expand=True, color=DIM if t["completed"] else TEXT,
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH if t["completed"]
                                else ft.TextDecoration.NONE)),
                ])
                for t in s["today_tasks"]
            ]
        else:
            task_rows = [empty_state(ft.Icons.TASK_ALT, "No tasks for today",
                                     "Open the Tasks tab to plan your study session.")]
        return ft.ListView(
            expand=True, spacing=16,
            controls=[
                ft.Column([dim_text("Welcome back,", 16),
            ft.Text("Sai", size=28,
                   weight=ft.FontWeight.BOLD, color=CYAN)], spacing=0),
                card(ft.Row([
                    progress_ring(s["fraction"]),
                    ft.Column([
                        ft.Text("Overall DSA Completion", size=16,
                                weight=ft.FontWeight.W_600, color=TEXT),
                        dim_text(f"{s['completed']} of {s['total']} topics completed"),
                        bar(s["fraction"]),
                    ], expand=True, spacing=8),
                ], spacing=20)),
                ft.FilledButton(cont_label, icon=ft.Icons.PLAY_ARROW, on_click=go_continue,
                                style=ft.ButtonStyle(bgcolor=PURPLE, color="#FFFFFF"),
                                height=52),
                ft.Row([stat_tile("Total Topics", s["total"], BLUE),
                        stat_tile("Completed", s["completed"], GREEN)], spacing=12),
                ft.Row([stat_tile("In Progress", s["in_progress"], CYAN),
                        stat_tile("Pending", s["not_started"], AMBER)], spacing=12),
                card(ft.Row([
                    ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT, color=AMBER, size=40),
                    ft.Column([
                        ft.Text(f"{s['streak']} day streak", size=16,
                                weight=ft.FontWeight.W_600, color=TEXT),
                        dim_text("Complete a topic or task today to start a streak"
                                 if s["streak"] == 0
                                 else "Complete a topic or task each day to keep it going"),
                    ], expand=True, spacing=2),
                ], spacing=12)),
                card(ft.Column([
                    ft.Row([ft.Text("Today's Tasks", size=16, weight=ft.FontWeight.W_600,
                                    color=TEXT),
                            ft.TextButton("Manage", on_click=lambda e: switch_tab(2))],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    *task_rows,
                ])),
            ],
        )

    def toggle_task_home(task_id, value):
        database.set_task_completed(task_id, bool(value))
        render()

    # =====================================================
    # ROADMAP
    # =====================================================
    def topic_row(t, refresh):
        done = t["status"] == dbm.COMPLETED

        def on_check(e):
            database.set_topic_status(
                t["id"], dbm.COMPLETED if e.control.value else dbm.NOT_STARTED)
            refresh()

        return ft.Container(
            content=ft.Row([
                ft.Checkbox(value=done, on_change=on_check),
                ft.Column([
                    ft.Text(t["title"], color=DIM if done else TEXT, size=15,
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH if done
                                else ft.TextDecoration.NONE)),
                    ft.Text("Has notes", size=11, color=PURPLE, visible=bool(t["notes"])),
                ], expand=True, spacing=0),
                ft.Text(dbm.STATUS_LABELS[t["status"]], size=11,
                        color=STATUS_COLORS[t["status"]]),
                ft.Icon(ft.Icons.EDIT_NOTE, color=DIM, size=20),
            ], spacing=6),
            bgcolor=SURFACE_HI, border_radius=14, padding=ft.padding.only(right=10),
            on_click=lambda e: open_topic_dialog(t["id"], refresh),
        )

    def open_topic_dialog(topic_id, refresh):
        t = next(x for x in database.topics() if x["id"] == topic_id)
        group = ft.RadioGroup(
            value=str(t["status"]),
            content=ft.Column([
                ft.Radio(value=str(dbm.NOT_STARTED), label="Not Started"),
                ft.Radio(value=str(dbm.IN_PROGRESS), label="In Progress"),
                ft.Radio(value=str(dbm.COMPLETED), label="Completed"),
            ], tight=True),
        )
        notes = ft.TextField(label="Personal notes", value=t["notes"], multiline=True,
                             min_lines=3, max_lines=6)
        completed_text = (f"Completed on {dbm.format_millis(t['completed_at'])}"
                          if t["completed_at"] else "Not completed yet")

        def save(e):
            database.set_topic_status(topic_id, int(group.value))
            database.save_topic_notes(topic_id, notes.value or "")
            page.close(dlg)
            refresh()

        dlg = ft.AlertDialog(
            title=ft.Text(t["title"]),
            content=ft.Column([group, dim_text(completed_text), notes],
                              tight=True, scroll=ft.ScrollMode.AUTO, width=320),
            actions=[ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                     ft.TextButton("Save", on_click=save)],
        )
        page.open(dlg)

    def section_tile(sec):
        sid, title, subtitle = sec
        topics = database.topics(sid)
        completed = sum(1 for t in topics if t["status"] == dbm.COMPLETED)

        def refresh():
            # Rebuild only this section (keeps scroll position) and the header.
            index = [s[0] for s in SECTIONS].index(sid)
            state["roadmap_list"].controls[index + 1] = section_tile(sec)
            update_roadmap_header()
            page.update()

        controls = []
        current_group = None
        for t in topics:
            if t["group_name"] != current_group:
                current_group = t["group_name"]
                if current_group:
                    controls.append(ft.Text(current_group.upper(), size=12, color=CYAN,
                                            weight=ft.FontWeight.BOLD))
            controls.append(topic_row(t, refresh))

        def on_expand(e):
            if e.data == "true":
                state["expanded"].add(sid)
            else:
                state["expanded"].discard(sid)

        return ft.Container(
            key=f"sec{sid}",
            bgcolor=SURFACE, border=ft.border.all(1, OUTLINE), border_radius=20,
            content=ft.ExpansionTile(
                title=ft.Text(f"{sid}. {title}", weight=ft.FontWeight.W_600, color=TEXT),
                subtitle=ft.Text(f"{completed} / {len(topics)} completed", color=DIM, size=12),
                initially_expanded=sid in state["expanded"],
                on_change=on_expand,
                controls=[ft.Container(
                    content=ft.Column(
                        [bar(completed / len(topics) if topics else 0, height=6),
                         *controls], spacing=8),
                    padding=ft.padding.only(left=12, right=12, bottom=12))],
                shape=ft.RoundedRectangleBorder(radius=20),
                collapsed_shape=ft.RoundedRectangleBorder(radius=20),
            ),
        )

    def update_roadmap_header():
        s = database.stats()
        header = state["roadmap_header"]
        header.controls[1].value = f"{s['completed']} of {s['total']} topics completed"
        header.controls[2].value = s["fraction"]

    def build_roadmap():
        s = database.stats()
        header = ft.Column([
            title_text("DSA Roadmap", 28),
            dim_text(f"{s['completed']} of {s['total']} topics completed"),
            bar(s["fraction"]),
        ], spacing=8)
        state["roadmap_header"] = header
        lv = ft.ListView(expand=True, spacing=12,
                         controls=[header] + [section_tile(sec) for sec in SECTIONS])
        state["roadmap_list"] = lv
        return lv

    # =====================================================
    # TASKS
    # =====================================================
    def build_tasks():
        t0 = dbm.today()
        tasks = database.tasks()
        filters = {
            "today": ("Today", [t for t in tasks if t["due_day"] == t0]),
            "pending": ("Pending", [t for t in tasks if not t["completed"]]),
            "done": ("Done", [t for t in tasks if t["completed"]]),
            "all": ("All", tasks),
        }
        current = state["task_filter"]

        def set_filter(key):
            state["task_filter"] = key
            render()

        chips = ft.Row(
            [ft.ElevatedButton(
                f"{label} ({len(items)})",
                on_click=lambda e, k=key: set_filter(k),
                bgcolor=PURPLE if key == current else SURFACE_HI,
                color="#FFFFFF" if key == current else DIM)
             for key, (label, items) in filters.items()],
            scroll=ft.ScrollMode.AUTO, spacing=8)

        shown = filters[current][1]
        empty_titles = {"today": "Nothing due today", "pending": "No pending tasks",
                        "done": "No completed tasks yet", "all": "No tasks yet"}

        if shown:
            rows = [task_row(t, t0) for t in shown]
        else:
            rows = [empty_state(ft.Icons.TASK_ALT, empty_titles[current],
                                'Tap + to add one, e.g. "Learn Arrays" or '
                                '"Solve 3 coding problems".')]

        return ft.Column([
            title_text("Daily Tasks", 28),
            dim_text("Plan and track your study sessions"),
            chips,
            ft.ListView(controls=rows, expand=True, spacing=10,
                        padding=ft.padding.only(bottom=88)),
        ], expand=True, spacing=10)

    def task_row(t, t0):
        overdue = (not t["completed"]) and t["due_day"] < t0
        if overdue:
            due = f"Overdue · {dbm.format_day(t['due_day'])}"
        elif t["due_day"] == t0:
            due = "Due today"
        else:
            due = f"Due {dbm.format_day(t['due_day'])}"

        def on_check(e):
            database.set_task_completed(t["id"], bool(e.control.value))
            render()

        def delete():
            database.delete_task(t["id"])
            render()

        return card(ft.Row([
            ft.Checkbox(value=bool(t["completed"]), on_change=on_check),
            ft.Column([
                ft.Text(t["title"], size=15, color=DIM if t["completed"] else TEXT,
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.LINE_THROUGH if t["completed"]
                            else ft.TextDecoration.NONE)),
                ft.Row([
                    ft.Text(dbm.PRIORITY_LABELS[t["priority"]].upper(), size=11,
                            weight=ft.FontWeight.BOLD, color=PRIORITY_COLORS[t["priority"]]),
                    ft.Text(due, size=12, color=RED if overdue else DIM),
                ], spacing=10),
            ], expand=True, spacing=2),
            ft.IconButton(ft.Icons.EDIT, icon_color=DIM, tooltip="Edit",
                          on_click=lambda e: open_task_dialog(t)),
            ft.IconButton(ft.Icons.DELETE, icon_color=RED, tooltip="Delete",
                          on_click=lambda e: confirm(
                              "Delete task?", f'"{t["title"]}" will be permanently deleted.',
                              "Delete", delete)),
        ], spacing=0), padding=8)

    def open_task_dialog(task=None):
        chosen = {"day": task["due_day"] if task else dbm.today()}
        title = ft.TextField(label="Task", value=task["title"] if task else "",
                             autofocus=True)
        priority = ft.Dropdown(
            label="Priority",
            value=str(task["priority"] if task else dbm.MEDIUM),
            options=[ft.dropdown.Option(key=str(k), text=v)
                     for k, v in dbm.PRIORITY_LABELS.items()])
        due_btn = ft.OutlinedButton(f"Due: {dbm.format_day(chosen['day'])}",
                                    icon=ft.Icons.DATE_RANGE)

        def on_date(e):
            if e.control.value:
                chosen["day"] = e.control.value.date().toordinal()
                due_btn.text = f"Due: {dbm.format_day(chosen['day'])}"
                due_btn.update()

        picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1), last_date=datetime(2100, 12, 31),
            value=datetime.combine(date.fromordinal(chosen["day"]), datetime.min.time()),
            on_change=on_date)
        due_btn.on_click = lambda e: page.open(picker)

        def save(e):
            if not (title.value or "").strip():
                title.error_text = "Please enter a task title"
                title.update()
                return
            prio = int(priority.value or dbm.MEDIUM)
            if task is None:
                database.add_task(title.value, prio, chosen["day"])
            else:
                database.update_task(task["id"], title.value, prio, chosen["day"])
            page.close(dlg)
            render()

        dlg = ft.AlertDialog(
            title=ft.Text("Add task" if task is None else "Edit task"),
            content=ft.Column([title, priority, due_btn], tight=True, width=320, spacing=14),
            actions=[ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                     ft.TextButton("Save", on_click=save)],
        )
        page.open(dlg)

    # =====================================================
    # PROGRESS
    # =====================================================
    def build_progress():
        s = database.stats()
        max_count = max([d["count"] for d in s["weekly"]] + [1])
        chart_h = 110

        week_cols = []
        for d in s["weekly"]:
            h = 4 if d["count"] == 0 else max(4, int(chart_h * d["count"] / max_count))
            week_cols.append(ft.Column([
                ft.Text(str(d["count"]), size=11, color=TEXT if d["count"] else DIM),
                ft.Container(height=h, border_radius=8,
                             bgcolor=PURPLE if d["count"] else TRACK, expand=False),
                ft.Text(d["label"], size=11, color=CYAN if d["is_today"] else DIM),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END, spacing=4))

        section_rows = []
        for sec in s["sections"]:
            frac = sec["completed"] / sec["total"] if sec["total"] else 0
            section_rows.append(ft.Column([
                ft.Row([ft.Text(sec["title"], size=13, color=TEXT, expand=True),
                        dim_text(f"{sec['completed']}/{sec['total']}", 12)]),
                bar(frac, PURPLE, 7),
            ], spacing=4))

        if s["recent"]:
            recent_rows = [ft.Row([
                ft.Text(t["title"], size=13, color=TEXT, expand=True),
                dim_text(dbm.format_millis(t["completed_at"]) if t["completed_at"] else "", 12),
            ]) for t in s["recent"]]
        else:
            recent_rows = [dim_text("No topics completed yet. Tick a topic in the Roadmap "
                                    "to see it here.")]

        def legend(label, value, color):
            return ft.Row([ft.Container(width=10, height=10, border_radius=5, bgcolor=color),
                           dim_text(label), ft.Container(expand=True),
                           ft.Text(str(value), color=TEXT)], spacing=8)

        return ft.ListView(expand=True, spacing=16, controls=[
            ft.Column([title_text("Progress", 28),
                       dim_text("Calculated from your saved activity")], spacing=2),
            card(ft.Row([
                progress_ring(s["fraction"]),
                ft.Column([
                    ft.Text("Overall Roadmap", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                    legend("Completed", s["completed"], GREEN),
                    legend("In progress", s["in_progress"], BLUE),
                    legend("Pending", s["not_started"], AMBER),
                ], expand=True, spacing=6),
            ], spacing=20)),
            ft.Row([stat_tile("Day Streak", s["streak"], AMBER),
                    stat_tile("Learning Days", s["learning_days"], CYAN)], spacing=12),
            ft.Row([stat_tile("Tasks Completed", s["tasks_completed"], GREEN),
                    stat_tile("Tasks Pending", s["tasks_pending"], PURPLE)], spacing=12),
            card(ft.Column([
                ft.Text("Weekly Activity", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                dim_text("Topics and tasks completed in the last 7 days"),
                ft.Row(week_cols, spacing=8, vertical_alignment=ft.CrossAxisAlignment.END,
                       height=chart_h + 50),
            ])),
            card(ft.Column([
                ft.Text("Section Progress", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                *section_rows,
            ], spacing=12)),
            card(ft.Column([
                ft.Text("Recently Completed", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                *recent_rows,
                ft.Text(f"{s['not_started'] + s['in_progress']} topics still pending",
                        size=13, color=AMBER),
            ], spacing=8)),
        ])

    # =====================================================
    # PROFILE
    # =====================================================
    def build_profile():
        p = database.profile()
        learning_days = database.stats()["learning_days"]

        username = ft.TextField(label="Username", value=p["username"])
        goal = ft.TextField(label="Learning goal", value=p["goal"], multiline=True,
                            min_lines=2, max_lines=3)
        language = ft.Dropdown(label="Preferred programming language", value=p["language"],
                               options=[ft.dropdown.Option(key=l, text=l) for l in LANGUAGES])
        target_label = ft.Text(f"Daily study target: {p['daily_target']} min", color=TEXT)

        def on_slide(e):
            target_label.value = f"Daily study target: {int(e.control.value)} min"
            target_label.update()

        target = ft.Slider(min=15, max=240, divisions=15, value=p["daily_target"],
                           label="{value} min", on_change=on_slide)

        def save(e):
            database.save_profile(username.value or "", goal.value or "",
                                  language.value or p["language"], int(target.value))
            snack("Profile saved")

        def do_reset():
            database.reset_progress()
            snack("Progress reset")
            render()

        return ft.ListView(expand=True, spacing=16, controls=[
            ft.Column([title_text("Profile", 28), dim_text("Your learning preferences")],
                      spacing=2),
            card(ft.Column([dim_text("Total learning days"),
                            ft.Text(str(learning_days), size=28, weight=ft.FontWeight.BOLD,
                                    color=CYAN)], spacing=2)),
            card(ft.Column([
                username, goal, language, target_label, target,
                ft.FilledButton("Save profile", on_click=save,
                                style=ft.ButtonStyle(bgcolor=PURPLE, color="#FFFFFF")),
            ], spacing=14)),
            card(ft.Column([
                ft.Text("Danger zone", size=16, weight=ft.FontWeight.W_600, color=RED),
                dim_text("Reset sets every topic back to Not Started and clears notes, "
                         "completion dates and activity history. Your tasks are kept."),
                ft.OutlinedButton(
                    "Reset progress",
                    style=ft.ButtonStyle(color=RED),
                    on_click=lambda e: confirm(
                        "Reset all progress?",
                        "This cannot be undone. All topic statuses, notes, completion dates "
                        "and activity history will be cleared.",
                        "Reset", do_reset)),
            ], spacing=10)),
        ])

    # =====================================================
    # navigation
    # =====================================================
    builders = [build_home, build_roadmap, build_tasks, build_progress, build_profile]

    fab = ft.FloatingActionButton(icon=ft.Icons.ADD, bgcolor=PURPLE,
                                  on_click=lambda e: open_task_dialog(None))

    def render():
        body.content = builders[state["tab"]]()
        page.floating_action_button = fab if state["tab"] == 2 else None
        page.update()
        focus = state["focus"]
        if state["tab"] == 1 and focus:
            state["focus"] = None
            try:
                state["roadmap_list"].scroll_to(key=f"sec{focus}", duration=300)
            except Exception:
                pass

    def show_tab(index):
        state["tab"] = index
        render()

    def switch_tab(index):
        nav.selected_index = index
        show_tab(index)

    nav = ft.NavigationBar(
        selected_index=0,
        bgcolor=SURFACE,
        indicator_color="#2B2160",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.MAP, label="Roadmap"),
            ft.NavigationBarDestination(icon=ft.Icons.TASK_ALT, label="Tasks"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Progress"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
        ],
        on_change=lambda e: show_tab(e.control.selected_index),
    )
    page.navigation_bar = nav
    page.add(ft.SafeArea(content=body, expand=True))
    render()


if __name__ == "__main__":
    ft.app(target=main)
