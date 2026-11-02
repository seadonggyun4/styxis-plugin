"""Agent evaluation must fail closed on client failure and untrusted model output."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('evaluate_agent',ROOT/'scripts/evaluate_agent.py')
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class AgentEvaluationBoundary(unittest.TestCase):
    def test_client_rejection_cannot_produce_a_perfect_selection_score(self):
        with tempfile.TemporaryDirectory() as td:
            work=Path(td)
            executable=work/'codex'
            executable.write_text('#!'+sys.executable+'\nimport sys,json\n'
                'if "--version" in sys.argv: print("codex-cli test-fixture");sys.exit(0)\n'
                'print(json.dumps({"type":"error","message":"model_not_found"}));sys.exit(1)\n')
            executable.chmod(0o755)
            report,observed=work/'result.json',work/'choices.jsonl'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_agent.py'),'--model','fixture',
                                   '--probe-only','--output',str(report),'--observations-out',str(observed)],
                                  env={**os.environ,'PATH':str(work)+os.pathsep+os.environ['PATH']},
                                  capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            data=json.loads(report.read_text())
            self.assertEqual(data['status'],'not_evaluated')
            self.assertEqual(data['observed_decisions'],0)
            self.assertIsNone(data['selection_rate'])
            self.assertEqual(observed.read_text(),'')

    def test_unknown_duplicate_partial_and_unretrieved_choices_are_rejected(self):
        queries=[{'id':'q1'},{'id':'q2'}]
        good={'query_id':'q1','ranking':['check_file'],'selected':['check_file']}
        for rows in [[good],[good,good],[{**good,'query_id':'unknown'}],
                     [{**good,'selected':['scan_pii']},{'query_id':'q2','ranking':[],'selected':[]}]]:
            with self.assertRaises(ValueError):
                agent.validate_choices({'observations':rows},queries,{'check_file','scan_pii'})

if __name__=='__main__':unittest.main()
