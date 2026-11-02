"""Metric and observation trust boundaries; no implementation-echo snapshots."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('evaluate', Path(__file__).parents[1]/'scripts/evaluate.py')
evaluate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluate)


class EvaluationContracts(unittest.TestCase):
    def test_multi_intent_hit_does_not_hide_missing_recall(self):
        m = evaluate.ranking_metrics(['wrong', 'a'], {'a':3, 'b':2}, 2)
        self.assertEqual(m['hit'], 1)
        self.assertEqual(m['recall'], .5)
        self.assertEqual(m['mrr'], .5)
        self.assertGreater(m['ndcg'], 0)
        self.assertLess(m['ndcg'], 1)
        self.assertIsNone(evaluate.ranking_metrics(['a'], {}, 3))

    def test_no_observations_never_becomes_perfect_score(self):
        query = {'id':'q', 'language':'en', 'kind':'negative', 'category':'edit', 'split':'holdout',
                 'relevant':{s:{} for s in evaluate.STAGES}}
        summary, _, failures, rows = evaluate.evaluate([query], {}, {})
        self.assertEqual(rows, [])
        self.assertEqual(failures, [])
        for stage in summary.values():
            self.assertIsNone(stage['correct_selection_rate']['value'])
            self.assertIsNone(stage['false_selection_rate']['value'])
            self.assertEqual(stage['observed_queries'], 0)

    def test_ranked_target_is_not_selection_and_negative_is_not_recall(self):
        query = {'id':'q', 'language':'ko', 'kind':'hard-negative', 'category':'schema', 'split':'development',
                 'relevant':{s:{} for s in evaluate.STAGES}}
        summary, _, _, _ = evaluate.evaluate([query], {}, {('q','tool'):{'ranking':['check_file']}})
        self.assertIsNone(summary['tool']['recall_at_3'])
        self.assertIsNone(summary['tool']['false_selection_rate']['value'])
        self.assertEqual(summary['tool']['negative_target_exposure_at_k'], 1)
        summary, _, failures, _ = evaluate.evaluate([query], {}, {('q','tool'):{'ranking':['check_file'], 'selected':['check_file']}})
        self.assertEqual(summary['tool']['false_selection_rate']['value'], 1)
        self.assertEqual(len(failures), 1)

    def test_observation_import_rejects_duplicates_unknowns_and_unretrieved_selection(self):
        candidates = {s:[{'id':'a'}, {'id':'b'}] for s in evaluate.STAGES}
        good = {'query_id':'q', 'stage':'tool', 'ranking':['a'], 'selected':[]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'observed.jsonl'
            for rows in [[good,good], [{**good,'query_id':'missing'}], [{**good,'ranking':['a','a']}],
                         [{**good,'ranking':['unknown']}], [{**good,'selected':['b']}]]:
                path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
                with self.assertRaises(ValueError):
                    evaluate.load_observations(path, {'q':{}}, candidates)
            path.write_text(json.dumps(good)+'\n')
            self.assertEqual(len(evaluate.load_observations(path, {'q':{}}, candidates)), 1)

if __name__ == '__main__':
    unittest.main()
