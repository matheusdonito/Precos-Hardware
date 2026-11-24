import unittest

from scripts.publish_snapshot import merge_snapshot_payloads


class SnapshotMergeTests(unittest.TestCase):
    def test_merge_preserves_both_runs_and_keeps_newest_observation_per_id(self):
        remote = {
            "generatedAt": "2026-11-24T13:20:00+00:00",
            "observations": [
                {"id": "same", "collectedAt": "2026-11-24T13:10:00+00:00", "price": 100},
                {"id": "remote-only", "collectedAt": "2026-11-23T13:10:00+00:00", "price": 80},
            ],
        }
        collected = {
            "generatedAt": "2026-11-24T13:30:00+00:00",
            "observations": [
                {"id": "same", "collectedAt": "2026-11-24T13:30:00+00:00", "price": 90},
                {"id": "collected-only", "collectedAt": "2026-11-24T13:30:00+00:00", "price": 70},
            ],
        }

        merged = merge_snapshot_payloads(remote, collected)

        self.assertEqual(
            {row["id"] for row in merged["observations"]},
            {"same", "remote-only", "collected-only"},
        )
        same = next(row for row in merged["observations"] if row["id"] == "same")
        self.assertEqual(same["price"], 90)
        self.assertEqual(merged["generatedAt"], "2026-11-24T13:30:00+00:00")

    def test_merge_keeps_remote_observation_when_it_is_newer(self):
        remote = {
            "generatedAt": "2026-11-24T13:40:00+00:00",
            "observations": [{"id": "same", "collectedAt": "2026-11-24T13:40:00+00:00", "price": 90}],
        }
        collected = {
            "generatedAt": "2026-11-24T13:30:00+00:00",
            "observations": [{"id": "same", "collectedAt": "2026-11-24T13:30:00+00:00", "price": 100}],
        }

        merged = merge_snapshot_payloads(remote, collected)

        self.assertEqual(merged["observations"][0]["price"], 90)
        self.assertEqual(merged["generatedAt"], "2026-11-24T13:40:00+00:00")


if __name__ == "__main__":
    unittest.main()
