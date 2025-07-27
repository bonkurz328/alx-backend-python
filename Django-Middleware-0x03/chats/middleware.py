import logging
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from collections import defaultdict

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

class RateLimitMiddleware:
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable and rate limit tracking."""
        self.get_response = get_response
        # Store request counts: {ip: [(timestamp, count)]}
        self.request_counts = defaultdict(list)
        self.MAX_MESSAGES = 5  # Max messages per minute
        self.TIME_WINDOW = 60  # Time window in seconds (1 minute)

    def __call__(self, request):
        """Limit POST requests to 5 per minute per IP address."""
        # Get client IP (handles cases behind proxies)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()

        # Only apply rate limiting to POST requests (assumed to be message submissions)
        if request.method == 'POST':
            current_time = datetime.now()
            # Clean up old requests outside the time window
            self.request_counts[ip] = [
                t for t in self.request_counts[ip]
                if (current_time - t[0]).total_seconds() <= self.TIME_WINDOW
            ]
            # Add current request timestamp
            self.request_counts[ip].append((current_time, 1))
            # Count requests in the time window
            request_count = len(self.request_counts[ip])

            # Check if limit is exceeded
            if request_count > self.MAX_MESSAGES:
                return HttpResponse(
                    "Rate limit exceeded: Only 5 messages allowed per minute.",
                    status=429  # Too Many Requests
                )

        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response

class RolePermissionMiddleware:
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """Restrict access to specific actions based on user role (admin or moderator)."""
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access denied: Authentication required.")

        # Check if user has admin or moderator role
        # Assuming user model has a 'role' field or is_staff/is_superuser for admin
        if not (request.user.is_staff or request.user.is_superuser):
            # If user model has a custom 'role' field, check for 'admin' or 'moderator'
            # Adjust based on your user model; example assumes a 'role' field
            try:
                if request.user.role not in ['admin', 'moderator']:
                    return HttpResponseForbidden("Access denied: Only admins or moderators allowed.")
            except AttributeError:
                # Fallback if 'role' field doesn't exist
                return HttpResponseForbidden("Access denied: Only admins or moderators allowed.")

        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response


