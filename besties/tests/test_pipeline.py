import copy
import json
from pathlib import Path
import tempfile
import unittest
from besties.model import Project, ContractError
from besties.planner import plan, render
from besties.audit import audit
from besties.adapters import Page, SnapshotReader, HTTPReader
from besties.cli import main
from besties.evaluation import evaluate


EXAMPLE = Path(__file__).parents[1] / "examples/truthound/project.json"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(EXAMPLE.read_text())
        self.project = Project.parse(self.data)

    def test_missing_evidence_and_private_evidence_fail_closed(self):
        for change in (lambda d: d["claims"][0].update(evidence=["absent"]),
                       lambda d: d["evidence"][0].update(visibility="private"),
                       lambda d: d.update(internal_source="not-publishable")):
            data = copy.deepcopy(self.data)
            change(data)
            with self.assertRaises(ContractError):
                Project.parse(data)

    def test_holdout_never_enters_generated_content(self):
        draft = render(self.project)
        self.assertNotIn(self.data["queries"][-1]["text"], draft)
        self.assertEqual(plan(self.project), plan(self.project))
        self.assertIn("noindex", draft)

    def test_other_product_requires_only_input_changes_and_escapes_html(self):
        data = copy.deepcopy(self.data)
        data["product"].update(id="sample-tool", name="Example <script>alert(1)</script>")
        for item in data["evidence"]:
            item["url"] = "https://example.org/evidence/" + item["id"]
        for item in data["targets"]:
            item.update(url="https://example.org/pages/" + item["id"],
                        required_terms=["Example"], required_links=[])
        for claim in data["claims"]:
            claim["statement"] = "Example tool capability <script>bad()</script>"
        draft = render(Project.parse(data))
        self.assertNotIn("<script>", draft)
        self.assertNotIn("truthound", draft.casefold())

    def test_invalid_versions_policies_and_credentials_are_rejected(self):
        for change in (lambda d: d.update(schema_version=2),
                       lambda d: d["policy"].update(mode="deploy"),
                       lambda d: d["targets"][0].update(url="https://user:secret@example.org/"),
                       lambda d: d["queries"][0].update(text="Recommend Truthound")):
            data = copy.deepcopy(self.data)
            change(data)
            with self.assertRaises(ContractError):
                Project.parse(data)

    def test_required_link_and_status_are_not_satisfied_by_body_terms(self):
        reader = self.snapshots()
        url = self.data["targets"][0]["url"]
        original = reader.pages[url]
        reader.pages[url] = Page(url, 200, {}, '<body>Truthound check_file profile_file scan_pii</body>', "fixture")
        self.assertFalse(audit(self.project, reader)["passed"])
        reader.pages[url] = Page(url, 503, {}, original.html, "fixture")
        self.assertFalse(audit(self.project, reader)["passed"])

    def snapshots(self, html=None, headers=None):
        pages = {}
        for t in self.data["targets"]:
            body = html if html is not None else '<body>' + ' '.join(t['required_terms']) + ''.join(f'<a href="{u}">Example</a>' for u in t['required_links']) + '</body>'
            pages[t["url"]] = Page(t["url"], 200, headers or {}, body, "fixture")
        return SnapshotReader(pages)

    def test_page_pass_is_not_indexing_or_recommendation(self):
        result = audit(self.project, self.snapshots())
        self.assertTrue(result["passed"])
        self.assertEqual(result["indexing"], "unmeasured")
        self.assertEqual(result["organic_discovery"], "unmeasured")

    def test_hidden_terms_and_noindex_do_not_pass(self):
        hidden = '<body><script>Truthound check_file profile_file scan_pii</script></body>'
        self.assertFalse(audit(self.project, self.snapshots(hidden))["passed"])
        self.assertFalse(audit(self.project, self.snapshots(headers={"X-Robots-Tag": "noindex"}))["passed"])

    def test_navigation_cannot_substitute_for_article_content(self):
        url = self.data["targets"][0]["required_links"][0]
        html = f'<body><nav>Truthound check_file profile_file scan_pii<a href="{url}">Example</a></nav><main><article>Framework overview only</article></main></body>'
        result = audit(self.project, self.snapshots(html))
        self.assertFalse(result["passed"])
        self.assertEqual(result["pages"][0]["content_region"], "article")
        self.assertIn("check_file", result["pages"][0]["missing_terms"])
        self.assertIn(url, result["pages"][0]["missing_links"])
        empty = html.replace("Framework overview only", "")
        self.assertFalse(audit(self.project, self.snapshots(empty))["passed"])

    def test_article_word_wrap_is_normalized(self):
        for target in self.data["targets"]:
            target["required_terms"] = ["local data validation"]
            target["required_links"] = []
        project = Project.parse(self.data)
        self.assertTrue(audit(project, self.snapshots('<body><article>local\n data\tvalidation</article></body>'))["passed"])

    def test_adapter_failure_is_unmeasured_and_does_not_leak_exception(self):
        class Broken:
            def read(self, url):
                raise OSError("sensitive local detail")
        result = audit(self.project, Broken())
        self.assertFalse(result["passed"])
        self.assertEqual(result["pages"][0]["status"], "unmeasured")
        self.assertNotIn("sensitive", json.dumps(result))

    def test_network_adapter_rejects_unconfigured_url_without_network(self):
        with self.assertRaises(ValueError):
            HTTPReader([]).read("https://example.com/")

    def test_cli_is_standalone_and_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "proposal"
            self.assertEqual(main(["plan", str(EXAMPLE), "--output", str(output)]), 0)
            before = (output / "draft.html").read_bytes()
            with self.assertRaises(SystemExit) as error:
                main(["plan", str(EXAMPLE), "--output", str(output)])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(before, (output / "draft.html").read_bytes())

    def test_prompted_and_unavailable_observations_are_not_organic_successes(self):
        observation = {"query_id":"category", "provider":"test", "surface":"ai_answer",
                       "observed_at":"2026-11-02T00:00:00Z", "status":"completed", "urls":[],
                       "brand_mentioned":True, "brand_prompted":True, "fresh_session":False}
        result = evaluate(self.project, [observation])
        self.assertFalse(result["observations"][0]["eligible_unbranded_observation"])
        observation.update(status="unavailable", brand_mentioned=False)
        with self.assertRaises(ContractError):
            evaluate(self.project, [observation])
        observation.update(brand_mentioned=None)
        self.assertIsNone(evaluate(self.project, [observation])["observations"][0]["configured_target_returned"])


if __name__ == "__main__":
    unittest.main()
