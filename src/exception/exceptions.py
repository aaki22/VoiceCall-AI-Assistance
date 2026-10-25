class AppException(Exception):
    code = "APP_ERROR"

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ExternalServiceException(AppException):
    code = "EXTERNAL_SERVICE_ERROR"


class LLMProviderException(ExternalServiceException):
    code = "LLM_PROVIDER_ERROR"


class AudioProcessingException(AppException):
    code = "AUDIO_PROCESSING_ERROR"


class PersistenceException(AppException):
    code = "PERSISTENCE_ERROR"


class ValidationException(AppException):
    code = "VALIDATION_ERROR"
