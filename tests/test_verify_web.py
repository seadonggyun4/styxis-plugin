"""A current string in hidden payloads must not validate stale public pages."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('verify_web', Path(__file__).resolve().parents[1]/'scripts/verify_web.py')
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


class ServedPageBoundary(unittest.TestCase):
    def test_hidden_current_version_and_similar_version_cannot_validate_old_body(self):
        for visible in ['Core 3.3.0', 'Core 3.3.10', 'Core 3.3.1-dev', 'Core 3.3.0. Footer: Core 3.3.1']:
            page = web.Inspect()
            page.feed(f'<body><p>{visible}</p><script>Core 3.3.1</script></body>')
            self.assertFalse(web.visible_core_version(page, '3.3.1'))
        page = web.Inspect()
        page.feed('<body><p>Core 3.3.1. 실제 실행 결과입니다.</p></body>')
        self.assertTrue(web.visible_core_version(page, '3.3.1'))

    def test_search_exclusion_is_a_failure_even_with_readable_body(self):
        page = web.Inspect()
        page.feed('<head><meta name="robots" content="follow, NOINDEX"></head><body>Current data validation MCP</body>')
        with self.assertRaisesRegex(AssertionError, 'page_noindex'):
            web.require_indexable(page)
