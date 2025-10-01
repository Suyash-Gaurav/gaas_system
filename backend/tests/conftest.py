import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Create temporary directory for test policies
    test_dir = tempfile.mkdtemp()
    os.environ["POLICY_STORAGE_PATH"] = test_dir
    os.environ["LOG_FILE"] = os.path.join(test_dir, "test.log")

    yield

    # Cleanup after tests
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    from fastapi.testclient import TestClient
    from backend.app.main import app

    return TestClient(app)
