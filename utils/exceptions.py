"""Custom domain exceptions for AI Study Buddy."""


class StudyBuddyError(Exception):
    """Base exception for all AI Study Buddy application errors."""


class ConfigurationError(StudyBuddyError):
    """Raised when required configuration (such as API key) is missing or invalid."""


class ValidationError(StudyBuddyError):
    """Raised when user input or uploaded file fails validation."""


class FileProcessingError(StudyBuddyError):
    """Raised when reading or extracting text from an uploaded file fails."""


class GeminiAPIError(StudyBuddyError):
    """Raised when communicating with the Gemini API fails."""


class GeminiAuthError(GeminiAPIError):
    """Raised when the Gemini API key is rejected or unauthorized."""


class GeminiRateLimitError(GeminiAPIError):
    """Raised when Gemini API quota or rate limits are exceeded."""


class QuizParseError(StudyBuddyError):
    """Raised when AI quiz output cannot be parsed or fails schema validation."""
