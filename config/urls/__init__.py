"""
Main URL configuration - imports from studio URLs as default
This is used as ROOT_URLCONF fallback
"""

from config.urls.studio import urlpatterns

__all__ = ['urlpatterns']

