# HTTP client errors
CONNECTION_ERROR = "Connection error in request"
CONNECTION_TIMEOUT = "Request connection timeout"
REQUEST_EXCEPTION = "Unexpected error from request"

# CSRF Token errors
INVALID_TOKEN = "Invalid CSRF Token"
TOKEN_COOKIE_ERROR = "Missing CSRF Token Cookie"
TOKEN_HEADER_ERROR = "Missing CSRF Token Header"
TOKEN_SIGNATURE_ERROR = "CSRF Token signatures do not match"
EXPIRED_TOKEN = "CSRF token has expired"

# Scopus API errors
QUOTA_EXCEEDED = "API Key has exceeded the request quota"
RATE_LIMIT_EXCEEDED = "Request rate limit per second exceeded"
VALIDATE_ERROR = "Error in validate response from Scopus API"
INVALID_JSON_ERROR = "Invalid JSON response from Scopus API"
SCOPUS_API_ERROR = "Scopus API error"
DATA_MISMATCH_ERROR = "Data sum mismatch in response"

# Application errors
CANCELLED_ERROR = "Unexpected cancellation of the tasks"
INTERNAL_ERROR = "Unexpected internal error occurred"
SERIALIZE_ERROR = "Error serializing error details"
ARTICLES_NOT_FOUND = "No articles found"
CSV_NOT_FOUND = "No CSV file found"
UNEXPECTED_ERROR = "An unexpected error occurred"
SLOWAPI_RATE_ERROR = "Request rate limit exceeded"
