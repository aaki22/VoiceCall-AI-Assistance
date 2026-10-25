from src.exception.exceptions import AppException, ExternalServiceException


def test_app_exception_exposes_code_and_details():
    exc = AppException("message", "details")

    assert exc.code == "APP_ERROR"
    assert exc.message == "message"
    assert exc.details == "details"


def test_external_service_exception_code():
    assert ExternalServiceException("x").code == "EXTERNAL_SERVICE_ERROR"
