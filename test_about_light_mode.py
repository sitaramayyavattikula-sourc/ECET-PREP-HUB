import unittest
import os
import re
from app import app

class TestAboutLightModeVisibility(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_about_section_structure(self):
        """Verify that the home page contains the About section with all required elements."""
        res = self.app.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Check section and container IDs/classes
        self.assertIn('id="about"', html, "Missing #about anchor")
        self.assertIn('class="about"', html, "Missing .about section")
        self.assertIn('class="about-container"', html, "Missing .about-container")
        self.assertIn('class="about-text"', html, "Missing .about-text")

        # Check text contents
        self.assertIn("About ECET", html, "Missing main heading 'About ECET'")
        self.assertIn("Engineering Common Entrance Test (ECET)", html, "Missing section heading/subtitle")
        self.assertIn("ECET-PREPHUB is an integrated online learning platform", html, "Missing description paragraph")
        self.assertIn("High-quality Study Notes", html, "Missing feature checklist item")
        self.assertIn("Previous Year Question Papers", html, "Missing feature checklist item")
        self.assertIn("Online Practice Quizzes", html, "Missing feature checklist item")
        self.assertIn("Performance Tracking", html, "Missing feature checklist item")
        print("[OK] About section elements and content verified in index.html")

    def test_about_light_mode_css_rules(self):
        """Verify that style.css contains targeted, high-contrast light mode styling for About section."""
        css_path = os.path.join(app.static_folder, "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Check light-mode scoped tokens
        self.assertIn("--text-primary: #172033;", css)
        self.assertIn("--text-secondary: #334155;", css)
        self.assertIn("--text-muted: #64748B;", css)

        # Check main heading color #172033 (dark navy)
        self.assertTrue(
            re.search(r'html\[data-theme="light"\]\s+\.about\s+h2[^{]*\{[^}]*color:\s*#172033', css) or
            re.search(r'\.about-text\s+h2[^{]*\{[^}]*color:\s*#172033', css) or
            re.search(r':root\s+\.about\s+h2[^{]*\{[^}]*color:\s*#172033', css),
            "Main heading #172033 rule missing in light mode"
        )

        # Check section heading color #1E293B (strong dark slate)
        self.assertTrue(
            re.search(r'html\[data-theme="light"\]\s+\.about\s+h3[^{]*\{[^}]*color:\s*#1E293B', css) or
            re.search(r'\.about-text\s+h3[^{]*\{[^}]*color:\s*#1E293B', css) or
            re.search(r':root\s+\.about\s+h3[^{]*\{[^}]*color:\s*#1E293B', css),
            "Section heading #1E293B rule missing in light mode"
        )

        # Check body text color #334155 (dark slate)
        self.assertTrue(
            re.search(r'html\[data-theme="light"\]\s+\.about\s+p[^{]*\{[^}]*color:\s*#334155', css) or
            re.search(r'\.about-text\s+p[^{]*\{[^}]*color:\s*#334155', css) or
            re.search(r':root\s+\.about\s+p[^{]*\{[^}]*color:\s*#334155', css),
            "Body text #334155 rule missing in light mode"
        )

        # Check list item color #1E293B
        self.assertTrue(
            re.search(r'html\[data-theme="light"\]\s+\.about\s+li[^{]*\{[^}]*color:\s*#1E293B', css) or
            re.search(r'\.about-text\s+li[^{]*\{[^}]*color:\s*#1E293B', css) or
            re.search(r':root\s+\.about\s+li[^{]*\{[^}]*color:\s*#1E293B', css),
            "List item #1E293B rule missing in light mode"
        )

        # Check secondary / supporting text color #64748B
        self.assertTrue(
            re.search(r'html\[data-theme="light"\]\s+\.about\s+\.subtitle[^{]*\{[^}]*color:\s*#64748B', css) or
            re.search(r'\.about\s+small[^{]*\{[^}]*color:\s*#64748B', css) or
            re.search(r'\.about-text\s+small[^{]*\{[^}]*color:\s*#64748B', css),
            "Supporting text #64748B rule missing in light mode"
        )

        # Verify dark mode rules are preserved intact
        self.assertIn('html[data-theme="dark"] .about-section', css)
        self.assertIn('html[data-theme="dark"] .about-container', css)
        self.assertIn('html[data-theme="dark"] .about-content h2', css)
        self.assertIn('html[data-theme="dark"] .about-content p', css)
        print("[OK] CSS rules verified: Light Mode has high-contrast colors and Dark Mode is strictly preserved")

    def test_theme_toggle_persistence_script(self):
        """Verify theme.js supports light and dark mode toggling seamlessly."""
        js_path = os.path.join(app.static_folder, "js", "theme.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("ecet-prephub-theme", js)
        self.assertIn("applyTheme", js)
        self.assertIn("toggleTheme", js)
        self.assertIn("data-theme", js)
        print("[OK] Theme toggle script integrity confirmed")

if __name__ == "__main__":
    unittest.main()
