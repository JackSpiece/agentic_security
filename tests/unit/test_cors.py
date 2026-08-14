from fastapi import FastAPI
from fastapi.testclient import TestClient

from agentic_security.middleware.cors import setup_cors


def test_wildcard_cors_does_not_allow_credentials():
    app = FastAPI()
    setup_cors(app)

    @app.get("/test")
    async def test_route():
        return {"ok": True}

    client = TestClient(app)
    response = client.options(
        "/test",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in response.headers
