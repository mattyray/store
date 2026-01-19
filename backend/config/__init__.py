# Celery app - only import for worker processes to avoid blocking web startup
# The web server doesn't need the Celery app loaded at startup
__all__ = ()
