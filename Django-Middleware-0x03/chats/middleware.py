import logging
from datetime import datetime
from django.http import HttpResponseForbidden

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

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """Restrict access based on time (allow only between 6 PM and 9 PM)."""
        current_hour = datetime.now().hour
        # Check if current time is outside 6 PM (18:00) to 9 PM (21:00)
        if not (18 <= current_hour < 21):
            return HttpResponseForbidden("Access to the messaging app is restricted outside of 6 PM to 9 PM.")
        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response
