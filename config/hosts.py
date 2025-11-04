"""
Django Hosts configuration for subdomain routing

Base domain (provokely.com) → Studio/Hub landing page
Subdomain (reviewsocial.provokely.com) → ReviewSocial Shopify app
"""

from django_hosts import patterns, host

host_patterns = patterns(
    '',
    # Subdomain for ReviewSocial Shopify app
    host(r'reviewsocial', 'reviewsocial.urls', name='reviewsocial'),
    
    # Base domain for Provokely studio hub
    host(r'www', 'config.urls.studio', name='www'),
    host(r'', 'config.urls.studio', name='base'),  # Without www
)

