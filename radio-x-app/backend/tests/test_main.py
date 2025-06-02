import pytest
from app.main import app  # Assuming your Flask app instance is named 'app'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the /api/health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok", "message": "Backend is running!"}
