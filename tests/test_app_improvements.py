import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.core.dependencies as dependencies
import app.db.session as database
from app.core.config import Settings, settings
from app.main import app
from app.models import Base


class AppImprovementsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.original_auto_create_tables = settings.AUTO_CREATE_TABLES
        settings.AUTO_CREATE_TABLES = False

        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            db: Session = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[database.get_db] = override_get_db
        app.dependency_overrides[dependencies.get_db] = override_get_db
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        settings.AUTO_CREATE_TABLES = self.original_auto_create_tables

    def test_settings_parse_comma_separated_origins(self) -> None:
        parsed = Settings(
            ALLOWED_ORIGINS=["http://localhost:3000, http://localhost:5173"])
        self.assertEqual(
            parsed.ALLOWED_ORIGINS,
            ["http://localhost:3000", "http://localhost:5173"],
        )

    def test_health_alias_adds_process_time_header(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertIn("X-Process-Time", response.headers)

    def test_versioned_auth_login_and_profile(self) -> None:
        register_response = self.client.post(
            "/api/v1/auth/register/admin",
            json={
                "admin_id": "ADM001",
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "admin123456",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "admin123456",
            },
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]

        me_response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(
            me_response.json(),
            {
                "id": 1,
                "email": "admin@example.com",
                "name": "Admin User",
                "role": "admin",
                "is_active": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
