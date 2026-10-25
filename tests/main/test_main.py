from src.main import create_app


def test_create_app_registers_expected_routes():
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/inbound" in paths
    assert "/process-recording" in paths
    assert "/health" in paths
    assert "/health/db" in paths
