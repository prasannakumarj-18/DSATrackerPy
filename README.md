# DSA Tracker (Python / Flet version)

Same app as the Kotlin version: 11 roadmap sections from your PDF (90+ topics), topic status + notes +
completion date, daily tasks, progress charts, streak, profile. Data is stored locally in SQLite, no internet needed.

## Run on your computer (easiest way to try it)

1. Install Python 3.10+ from https://www.python.org
2. Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   flet run src/main.py
   ```
   A desktop window opens. Use `flet run --android src/main.py` or `flet run --web src/main.py` for other targets.

## Build an Android APK

Needs internet, and about 10 GB free space (Flet downloads Flutter and the Android SDK pieces on first build).
Windows users: use Windows 10/11 with the Android build prerequisites described at https://flet.dev/docs/publish/android

```
pip install -r requirements.txt
flet build apk
```
The APK appears in `build/apk/`. Copy it to your phone and install it.

## Files

| File | Purpose |
|---|---|
| `src/main.py` | Entry point and all screens (Flet UI) |
| `src/db.py` | SQLite database, progress/streak calculations |
| `src/roadmap_data.py` | The roadmap topics from your PDF |
| `tests/test_logic.py` | Tests for the database and calculations: `python -m unittest discover -s tests` |

## Notes

- Reset progress clears topics, notes and activity; your tasks are kept.
- The data file is `src/storage/dsa_tracker.db` on desktop, and the app's private storage on Android.
- Built against Flet 0.28.3. Newer Flet versions changed parts of the API, so keep the pinned version.
