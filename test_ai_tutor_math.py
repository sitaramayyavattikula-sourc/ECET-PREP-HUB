import unittest
from app import app

class TestAITutorMathRendering(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        with self.client.session_transaction() as sess:
            sess['student_email'] = 'test@example.com'
            sess['student_name'] = 'Test Student'
            sess['student_branch'] = 'cme'

    def test_ai_tutor_page_served_with_katex(self):
        response = self.client.get('/ai_tutor')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        
        # Verify compiled dist assets are referenced
        self.assertIn('dist/main.css', html)
        self.assertIn('dist/main.js', html)
        
        # Verify renderMarkdown uses renderAIResponse
        self.assertIn('window.renderAIResponse', html)

    def test_dist_assets_exist_and_contain_katex(self):
        response_js = self.client.get('/static/dist/main.js')
        self.assertEqual(response_js.status_code, 200)
        js_content = response_js.data.decode('utf-8')
        self.assertIn('katex', js_content.lower())
        self.assertIn('renderAIResponse', js_content)

        response_css = self.client.get('/static/dist/main.css')
        self.assertEqual(response_css.status_code, 200)
        css_content = response_css.data.decode('utf-8')
        self.assertIn('katex', css_content.lower())

    def test_scoped_css_rules_in_dashboard_css(self):
        response_dash = self.client.get('/static/css/dashboard.css')
        self.assertEqual(response_dash.status_code, 200)
        css = response_dash.data.decode('utf-8')
        self.assertIn('.bubble-text .katex', css)
        self.assertIn('.bubble-text .katex-display', css)
        self.assertIn('overflow-x: auto', css)
        self.assertIn('html[data-theme="light"] .assistant-bubble .bubble-text .katex', css)

    def test_node_math_rendering_suite(self):
        import subprocess
        result = subprocess.run(['node', 'test_math_render.cjs'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Node test suite failed:\n{result.stderr}")
        self.assertIn('ALL AUTOMATED JS TESTS PASSED', result.stdout)

if __name__ == '__main__':
    unittest.main()
