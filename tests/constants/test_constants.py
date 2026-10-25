from src.constants.routes import HEALTH_PATH, INBOUND_PATH, PROCESS_RECORDING_PATH


def test_route_constants_are_stable():
    assert INBOUND_PATH == "/inbound"
    assert PROCESS_RECORDING_PATH == "/process-recording"
    assert HEALTH_PATH == "/health"
