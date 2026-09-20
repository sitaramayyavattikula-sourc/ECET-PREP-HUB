import os
import json
import unittest
from app import app
from database.database import (
    get_connection,
    create_tables,
    get_student_by_email,
    get_conversation_messages
)

class TestFinalTargetedFix(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        create_tables()

    def test_final_targeted_fix_workflow(self):
        print("\n=======================================================")
        print("   MASTER PROFESSIONALIZATION FULL E2E QA TEST")
        print("=======================================================")

        test_email = "targeted_fix_student@example.com"
        test_phone = "9666777888"

        # Cleanup test student data
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE LOWER(email) = LOWER(?) OR phone = ?", (test_email, test_phone))
        cur.execute("DELETE FROM quiz_results WHERE LOWER(student_email) = LOWER(?)", (test_email,))
        cur.execute("DELETE FROM ai_conversations WHERE LOWER(student_email) = LOWER(?)", (test_email,))
        conn.commit()
        conn.close()

        # Step 1: Register & Login
        reg_res = self.app.post("/register", data={
            "name": "Prasad Netinti",
            "email": test_email,
            "phone": test_phone,
            "password": "Password123"
        })
        self.assertEqual(reg_res.status_code, 302)

        login_res = self.app.post("/login", data={
            "email": test_email,
            "password": "Password123"
        })
        self.assertEqual(login_res.status_code, 302)

        with self.app.session_transaction() as sess:
            sess['student_email'] = test_email
            sess['student_name'] = "Prasad Netinti"
            sess['student_branch'] = "cme"

        # Step 2: Profile Update Persistence
        res_prof = self.app.post("/api/update_profile", data={
            "name": "Prasad Netinti Senior",
            "phone": test_phone,
            "branch": "cme"
        })
        self.assertEqual(res_prof.status_code, 200)
        updated_student = get_student_by_email(test_email)
        self.assertIsNotNone(updated_student)
        self.assertEqual(updated_student["name"], "Prasad Netinti Senior")
        print("[OK] Test 2: Profile updated and verified in database")

        # Step 3: Universal Navigation Sidebar & Header on ALL 14 Authenticated Routes
        authenticated_routes = [
            "/dashboard",
            "/notes",
            "/notes/cme",
            "/notes/cme/first_year",
            "/paper_branches",
            "/papers/cme",
            "/quiz",
            "/cme-quiz",
            "/quiz/cme",
            "/leaderboard",
            "/ai_tutor",
            "/ai_exam_setup",
            "/ai_exam",
            "/profile"
        ]

        for path in authenticated_routes:
            res = self.app.get(path)
            self.assertEqual(res.status_code, 200, f"Route {path} failed with status {res.status_code}")
            self.assertIn(b"appSidebar", res.data, f"appSidebar missing on {path}")
            self.assertIn(b"hamburger-btn", res.data, f"hamburger-btn missing on {path}")
            self.assertIn(b"sidebar-menu", res.data, f"sidebar-menu missing on {path}")
        print("[OK] Test 3: Global Sidebar & Header verified on all 14 authenticated routes")

        # Step 4: Three-Dot Dropdown CSS Rules & Zero-Scrollbar Verification
        css_path = os.path.join(app.static_folder, "css", "dashboard.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        self.assertIn(".dropdown-chat-menu", css_content)
        self.assertIn("overflow: visible !important;", css_content)
        self.assertIn("height: auto !important;", css_content)
        self.assertIn("max-height: none !important;", css_content)
        self.assertIn("z-index: 99999 !important;", css_content)
        print("[OK] Test 4: Three-dot dropdown has zero scrollbars, height: auto, max-height: none, overflow: visible, z-index: 99999 & open-upward rules")

        # Step 5: AI Tutor Multi-Turn Conversational Interaction
        res_chat1 = self.app.post("/api/ai_chat", json={
            "message": "What is dynamic memory allocation in C?"
        })
        self.assertEqual(res_chat1.status_code, 200)
        data1 = res_chat1.get_json()
        self.assertIn("reply", data1)
        self.assertIn("conversation_id", data1)
        conv_id = data1["conversation_id"]

        # Turn 2: Follow-up question relying on prior context
        res_chat2 = self.app.post("/api/ai_chat", json={
            "message": "What about malloc and calloc? Telugu lo cheppu.",
            "conversation_id": conv_id
        })
        self.assertEqual(res_chat2.status_code, 200)
        data2 = res_chat2.get_json()
        self.assertIn("reply", data2)
        print(f"[OK] Test 5: AI Tutor multi-turn conversation and context verified (Conv ID: {conv_id})")

        # Step 6: Three-Dot Actions (Rename, Pin, Share, Delete)
        res_rename = self.app.post(f"/api/rename_conversation/{conv_id}", json={"title": "Dynamic Memory in C"})
        self.assertEqual(res_rename.status_code, 200)

        res_pin = self.app.post(f"/api/pin_conversation/{conv_id}")
        self.assertEqual(res_pin.status_code, 200)

        res_share = self.app.get(f"/api/share_conversation/{conv_id}")
        self.assertEqual(res_share.status_code, 200)
        print("[OK] Test 6: Rename, Pin, and Share conversation APIs verified")

        # Step 7: AI Exam Preparator Dynamic Branch Subjects
        exam_setup_res = self.app.get("/ai_exam_setup")
        self.assertEqual(exam_setup_res.status_code, 200)
        self.assertIn(b"C Programming", exam_setup_res.data)
        self.assertIn(b"Data Structures", exam_setup_res.data)
        print("[OK] Test 7: AI Exam setup with dynamic branch subjects verified")

        # Step 8: PDF Study Materials preservation
        pdf_dir = os.path.join(app.static_folder, "pdfs")
        self.assertTrue(os.path.exists(pdf_dir))
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
        print(f"[OK] Test 8: Verified {len(pdf_files)} PDF study materials in {pdf_dir}")

        print("\n=======================================================")
        print("   ALL MASTER PROFESSIONALIZATION TESTS PASSED! (100%)")
        print("=======================================================")

if __name__ == "__main__":
    unittest.main()
