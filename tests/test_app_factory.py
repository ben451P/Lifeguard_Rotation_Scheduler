import os
import tempfile
import unittest

from src import create_app


class AppFactoryTests(unittest.TestCase):
    def test_create_app_serves_login_page(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

            app = create_app()
            app.config["TESTING"] = True

            with app.test_client() as client:
                response = client.get("/login")

                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Login", response.data)


if __name__ == "__main__":
    unittest.main()
