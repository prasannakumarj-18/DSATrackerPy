import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import db as dbm  # noqa: E402
from roadmap_data import SECTIONS, all_topics  # noqa: E402


class LogicTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "t.db")
        self.db = dbm.Database(self.path)

    def tearDown(self):
        self.db.conn.close()
        self.tmp.cleanup()

    def test_seed_and_no_duplicates(self):
        n = len(self.db.topics())
        self.assertEqual(n, len(all_topics()))
        self.assertEqual(len(SECTIONS), 11)
        self.db.seed()
        self.db.seed()
        self.assertEqual(len(self.db.topics()), n)

    def test_topic_progress_and_streak(self):
        t = self.db.topics()[0]
        self.db.set_topic_status(t["id"], dbm.COMPLETED)
        s = self.db.stats()
        self.assertEqual(s["completed"], 1)
        self.assertEqual(s["streak"], 1)
        self.assertEqual(s["learning_days"], 1)
        self.assertAlmostEqual(s["fraction"], 1 / s["total"])
        self.db.set_topic_status(t["id"], dbm.NOT_STARTED)
        s = self.db.stats()
        self.assertEqual((s["completed"], s["streak"], s["learning_days"]), (0, 0, 0))

    def test_in_progress_and_next_topic(self):
        topics = self.db.topics()
        self.db.set_topic_status(topics[3]["id"], dbm.IN_PROGRESS)
        s = self.db.stats()
        self.assertEqual(s["in_progress"], 1)
        self.assertEqual(s["next_topic"]["id"], topics[3]["id"])
        self.assertEqual(s["streak"], 0)

    def test_tasks_crud_and_activity(self):
        tid = self.db.add_task("Learn Arrays", dbm.HIGH, dbm.today())
        self.assertEqual(len(self.db.stats()["today_tasks"]), 1)
        self.db.update_task(tid, "Learn Arrays well", dbm.LOW, dbm.today() + 1)
        self.assertEqual(len(self.db.stats()["today_tasks"]), 0)
        self.db.set_task_completed(tid, True)
        s = self.db.stats()
        self.assertEqual((s["tasks_completed"], s["tasks_pending"], s["streak"]), (1, 0, 1))
        self.db.delete_task(tid)
        self.assertEqual(self.db.tasks(), [])

    def test_streak_function(self):
        self.assertEqual(dbm.compute_streak({10, 9, 8}, 10), 3)
        self.assertEqual(dbm.compute_streak({9, 8}, 10), 2)
        self.assertEqual(dbm.compute_streak({8}, 10), 0)

    def test_reset_keeps_tasks(self):
        t = self.db.topics()[0]
        self.db.set_topic_status(t["id"], dbm.COMPLETED)
        self.db.save_topic_notes(t["id"], "  hello ")
        self.db.add_task("x", dbm.LOW, dbm.today())
        self.db.reset_progress()
        s = self.db.stats()
        self.assertEqual((s["completed"], s["learning_days"]), (0, 0))
        self.assertEqual(self.db.topics()[0]["notes"], "")
        self.assertEqual(len(self.db.tasks()), 1)

    def test_persistence_and_profile(self):
        t = self.db.topics()[0]
        self.db.set_topic_status(t["id"], dbm.COMPLETED)
        self.db.save_profile("Asha", "Crack interviews", "Java", 90)
        self.db.conn.close()
        again = dbm.Database(self.path)
        self.assertEqual(again.stats()["completed"], 1)
        self.assertEqual(again.profile()["username"], "Asha")
        self.assertEqual(again.profile()["daily_target"], 90)
        again.conn.close()
        self.db = dbm.Database(self.path)


if __name__ == "__main__":
    unittest.main()
