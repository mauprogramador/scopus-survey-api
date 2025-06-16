# HTTP client errors
CONNECTION_ERROR = "Connection error in request"
CONNECTION_TIMEOUT = "Request connection timeout"
REQUEST_EXCEPTION = "Unexpected error from request"
CANCELLED_ERROR = "Request was cancelled"
CLIENT_EXCEPTION = "Unexpected client error in request"

# CSRF Token errors
MISSING_TOKEN = "Missing CSRF Token"
INVALID_TOKEN = "Invalid CSRF Token"
TOKEN_COOKIE_ERROR = "Missing CSRF Token Cookie"
TOKEN_HEADER_ERROR = "Missing or invalid CSRF Token Header"
TOKEN_SESSION_ERROR = "Missing or invalid CSRF Token Session"
TOKEN_SIGNATURE_ERROR = "CSRF Token signatures do not match"
EXPIRED_TOKEN = "CSRF token has expired"


# Scopus API errors
QUOTA_EXCEEDED = "API Key has exceeded the request quota"
RATE_LIMIT_EXCEEDED = "Request rate limit per second exceeded"
SEARCH_API_ERROR = "Invalid response from Scopus Search API"
ABSTRACT_API_ERROR = "Invalid response from Scopus Abstract Retrieval API"
VALIDATE_ERROR = "Error in validate response from Scopus API"
SCOPUS_API_ERROR = "Scopus API Error"

# Application errors
INTERRUPT_ERROR = "Unexpected interruption"
INTERNAL_ERROR = "Unexpected internal error occurred"
SERIALIZE_ERROR = "Error serializing error details"
ARTICLES_NOT_FOUND = "No articles found"
CSV_NOT_FOUND = "No CSV file found"
UNEXPECTED_ERROR = "An unexpected error occurred"
