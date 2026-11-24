from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WorkflowStructureTests(unittest.TestCase):
    def test_pages_deployment_has_a_single_owner(self):
        workflows = ROOT / ".github" / "workflows"
        yaml_files = workflows.glob("*.yml")
        pages_deployers = []
        for path in yaml_files:
            content = path.read_text(encoding="utf-8")
            if "actions/deploy-pages@" in content:
                pages_deployers.append(path.name)
        self.assertEqual(
            pages_deployers,
            ["pages.yml"],
            "GitHub Pages must be published only by the dedicated pages workflow",
        )

    def test_collector_workflow_does_not_require_pages_permissions(self):
        workflow = (ROOT / ".github" / "workflows" / "collect-prices.yml").read_text(encoding="utf-8")
        self.assertNotIn("pages: write", workflow)
        self.assertNotIn("id-token: write", workflow)

    def test_pages_workflow_republishes_after_successful_collection(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_run:", workflow)
        self.assertIn('workflows: ["Coletar preços do radar"]', workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)


if __name__ == "__main__":
    unittest.main()
