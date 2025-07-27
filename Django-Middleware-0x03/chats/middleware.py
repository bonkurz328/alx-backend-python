import logging
from datetime import datetime

# Configure logger for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('requests.log')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """Log request details and process the request."""
        # Get the user (use username if authenticated, else 'Anonymous')
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        # Log the timestamp, user, and request path
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response
