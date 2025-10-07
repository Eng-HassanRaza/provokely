"""
Instagram-specific service layer
"""
import requests
from urllib.parse import urlencode
from django.conf import settings
from core.services import SocialMediaService
from shared.interfaces import PlatformServiceInterface
from shared.exceptions import PlatformAPIError
from django.utils import timezone
from typing import Optional, List, Dict


class InstagramService(PlatformServiceInterface):
    """Instagram-specific service implementation"""
    
    def __init__(self):
        self.core_service = SocialMediaService()
    
    def fetch_posts(self, account_id: str, limit: int = 10):
        """Fetch posts from Instagram Graph API using IG user id."""
        base_url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{account_id}/media"
        params = {
            'fields': 'id,caption,media_type,permalink,timestamp',
            'limit': limit,
        }
        # access_token must be provided by caller via ensure_fresh_token and account storage
        if hasattr(self, '_access_token') and self._access_token:
            params['access_token'] = self._access_token
        else:
            raise PlatformAPIError("Access token not set for fetch_posts")
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get('data', [])
        except requests.Timeout:
            raise PlatformAPIError("Instagram API request timed out while fetching posts")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to fetch posts: {str(e)}")
    
    def fetch_comments(self, post_id: str):
        """Fetch comments for a specific Instagram media id."""
        base_url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{post_id}/comments"
        params = {
            'fields': 'id,text,username,timestamp',
        }
        if hasattr(self, '_access_token') and self._access_token:
            params['access_token'] = self._access_token
        else:
            raise PlatformAPIError("Access token not set for fetch_comments")
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get('data', [])
        except requests.Timeout:
            raise PlatformAPIError("Instagram API request timed out while fetching comments")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to fetch comments: {str(e)}")

    def fetch_comment_detail(self, comment_id: str):
        """Fetch a single comment detail (text, username, media)."""
        if not hasattr(self, '_access_token') or not self._access_token:
            raise PlatformAPIError("Access token not set for fetch_comment_detail")
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{comment_id}"
        params = {
            'fields': 'id,text,username,media{id}',
            'access_token': self._access_token,
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            raise PlatformAPIError("Instagram API request timed out while fetching comment detail")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to fetch comment detail: {str(e)}")
    
    def post_comment(self, post_id: str, text: str):
        """Post a top-level comment to an Instagram media (post)."""
        if not hasattr(self, '_access_token') or not self._access_token:
            raise PlatformAPIError("Access token not set for post_comment")
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{post_id}/comments"
        data = {
            'message': text,
            'access_token': self._access_token,
        }
        try:
            resp = requests.post(url, data=data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            raise PlatformAPIError("Instagram API request timed out while posting comment")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to post comment: {str(e)}")

    def post_reply(self, comment_id: str, text: str):
        """Post a reply to an existing Instagram comment."""
        if not hasattr(self, '_access_token') or not self._access_token:
            raise PlatformAPIError("Access token not set for post_reply")
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{comment_id}/replies"
        data = {
            'message': text,
            'access_token': self._access_token,
        }
        try:
            resp = requests.post(url, data=data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            raise PlatformAPIError("Instagram API request timed out while posting reply")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to post reply: {str(e)}")
    
    def get_authorization_url(self, state: str = None, redirect_uri: str | None = None):
        """
        Generate Facebook Login authorization URL for Instagram Business
        
        Args:
            state: Optional state parameter for security
        
        Returns:
            str: Authorization URL
        """
        params = {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'redirect_uri': redirect_uri or settings.INSTAGRAM_REDIRECT_URI,
            'scope': 'pages_show_list,instagram_basic,instagram_manage_comments,pages_manage_engagement,pages_read_engagement,pages_read_user_content',
            'response_type': 'code',
        }
        
        if state:
            params['state'] = state
            
        # Use Facebook Login for Instagram Business accounts
        base_url = f"https://www.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/dialog/oauth"
        # Properly URL-encode the parameters
        return f'{base_url}?{urlencode(params)}'
    
    def exchange_code_for_token(self, code: str, redirect_uri: str):
        """
        Exchange authorization code for access token via Facebook
        
        Args:
            code: Authorization code from Facebook
        
        Returns:
            dict: Token response
        """
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/oauth/access_token"
        params = {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'code': code,
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            
            return token_data
        except requests.Timeout:
            raise PlatformAPIError("Facebook API request timed out. Please try again.")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to exchange code for token: {str(e)}")
    
    def get_long_lived_token(self, short_lived_user_token: str):
        """
        Exchange short-lived Facebook User token for a long-lived token.
        Uses fb_exchange_token per Facebook Login docs (v23.0).
        """
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'fb_exchange_token': short_lived_user_token,
        }
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise PlatformAPIError("Facebook API request timed out. Please try again.")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to get long-lived token: {str(e)}")
    
    def refresh_long_lived_token(self, long_lived_user_token: str):
        """
        Re-exchange a long-lived token. Facebook does not provide a refresh endpoint;
        you can rotate by re-calling the fb_exchange_token flow when needed.
        """
        return self.get_long_lived_token(long_lived_user_token)

    def validate_permissions(self, access_token: str, required_scopes: list[str]) -> list[str]:
        """
        Validate that required scopes are granted for the user token.
        Returns a list of missing scopes (empty if all granted).
        """
        url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/me/permissions"
        params = { 'access_token': access_token }
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            granted = {p['permission'] for p in data.get('data', []) if p.get('status') == 'granted'}
            missing = [scope for scope in required_scopes if scope not in granted]
            if settings.DEBUG:
                print(f"Granted permissions: {sorted(list(granted))}")
                print(f"Missing permissions: {missing}")
            return missing
        except requests.RequestException as e:
            # If validation fails to fetch, don't block, but log/debug
            if settings.DEBUG:
                print(f"Permissions validation failed: {e}")
            return []
    
    def validate_facebook_token(self, access_token: str) -> dict:
        """
        Validate Facebook access token using Debug Token API.
        Used for mobile SDK flow where we receive token directly.
        
        Args:
            access_token: Facebook access token to validate
        
        Returns:
            dict: Token data including is_valid, app_id, expires_at, user_id, scopes
        
        Raises:
            PlatformAPIError: If token validation fails
        """
        url = "https://graph.facebook.com/debug_token"
        app_token = f"{settings.INSTAGRAM_CLIENT_ID}|{settings.INSTAGRAM_CLIENT_SECRET}"
        params = {
            'input_token': access_token,
            'access_token': app_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            token_data = data.get('data', {})
            
            if settings.DEBUG:
                print(f"Token validation: is_valid={token_data.get('is_valid')}, app_id={token_data.get('app_id')}")
            
            return token_data
        except requests.Timeout:
            raise PlatformAPIError("Facebook token validation timed out. Please try again.")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to validate Facebook token: {str(e)}")
    
    def get_user_profile(self, access_token: str):
        """
        Get Instagram business account information via Facebook Pages
        
        Args:
            access_token: Facebook access token
        
        Returns:
            dict: Instagram business account data
        """
        # First, get user's Facebook Pages (request page access_token)
        pages_url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/me/accounts"
        pages_params = {
            'access_token': access_token,
            'fields': 'id,name,instagram_business_account,access_token'
        }
        
        try:
            pages_response = requests.get(pages_url, params=pages_params, timeout=30)
            
            pages_response.raise_for_status()
            pages_data = pages_response.json()
            
            # Find the first page with an Instagram business account
            for page in pages_data.get('data', []):
                if 'instagram_business_account' in page:
                    ig_account_id = page['instagram_business_account']['id']
                    page_access_token = page.get('access_token') or access_token
                    
                    # Get Instagram business account details
                    ig_url = f"https://graph.facebook.com/{settings.FACEBOOK_GRAPH_VERSION}/{ig_account_id}"
                    # Request only fields guaranteed on IG User for this flow
                    ig_params = {
                        'access_token': page_access_token,
                        'fields': 'id,username,media_count'
                    }
                    
                    ig_response = requests.get(ig_url, params=ig_params, timeout=30)
                    
                    if ig_response.status_code == 400:
                        # Instagram account not accessible - likely not properly linked
                        error_data = ig_response.json()
                        raise PlatformAPIError(f"Instagram account not accessible. Please ensure your Instagram account is properly linked to a Facebook Page and is a Business account. Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
                    
                    ig_response.raise_for_status()
                    ig_data = ig_response.json()
                    
                    
                    return {
                        'id': ig_data.get('id'),
                        'username': ig_data.get('username'),
                        'account_type': 'BUSINESS',
                        'media_count': ig_data.get('media_count', 0),
                        'followers_count': ig_data.get('followers_count', 0),
                        'following_count': ig_data.get('follows_count', 0),
                    }
            
            
            
            raise PlatformAPIError("No Instagram business account found linked to Facebook Pages. Please ensure your Instagram account is properly linked to a Facebook Page.")
            
        except requests.Timeout:
            raise PlatformAPIError("Facebook API request timed out. Please check your internet connection and try again.")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to get user profile: {str(e)}")
    
    def authenticate(self, credentials: dict):
        """
        Authenticate with Instagram Business using Facebook Login
        
        Args:
            credentials: Dictionary containing authentication credentials
        
        Returns:
            dict: Authentication tokens and user data
        """
        try:
            # Exchange code for a short-lived User access token (Facebook Login)
            token_response = self.exchange_code_for_token(credentials['code'], credentials['redirect_uri'])
            access_token = token_response['access_token']
            
            # Validate permissions (best-effort)
            required_scopes = [
                'instagram_basic',
                'instagram_manage_comments',
                'pages_manage_engagement',
                'pages_read_engagement',
                'pages_show_list',
                'pages_read_user_content',
            ]
            missing_scopes = self.validate_permissions(access_token, required_scopes)
            if missing_scopes:
                raise PlatformAPIError(f"Missing required permissions: {', '.join(missing_scopes)}")

            # Exchange to a long-lived user token (recommended)
            try:
                long_lived_response = self.get_long_lived_token(access_token)
                access_token = long_lived_response.get('access_token', access_token)
                long_expires_in = long_lived_response.get('expires_in')
                token_type = long_lived_response.get('token_type', 'bearer')
            except Exception:
                # proceed with short-lived token
                pass
            
            # Get Instagram business account profile
            profile = self.get_user_profile(access_token)
            
            return {
                'access_token': access_token,
                'expires_in': long_expires_in or token_response.get('expires_in'),
                'token_type': token_type if 'token_type' in locals() else token_response.get('token_type', 'bearer'),
                'user_id': profile['id'],
                'username': profile['username'],
                'account_type': profile.get('account_type', 'BUSINESS'),
                'media_count': profile.get('media_count', 0),
                'followers_count': profile.get('followers_count', 0),
                'following_count': profile.get('following_count', 0),
            }
        except Exception as e:
            raise PlatformAPIError(f"Instagram Business authentication failed: {str(e)}")

    # ---------------- Token lifecycle helpers ----------------
    def bind_access_token(self, access_token: str):
        """Bind an access token to this service instance for subsequent calls."""
        self._access_token = access_token

    def get_token_expiry_dt(self, token_created_at, expires_in: Optional[int]) -> Optional[timezone.datetime]:
        if not token_created_at or not expires_in:
            return None
        return token_created_at + timezone.timedelta(seconds=expires_in)

    def should_refresh_token(self, token_created_at, expires_in: Optional[int], safety_margin_days: int = 7) -> bool:
        expiry_dt = self.get_token_expiry_dt(token_created_at, expires_in)
        if not expiry_dt:
            return False
        return expiry_dt <= timezone.now() + timezone.timedelta(days=safety_margin_days)

    def refresh_user_token(self, access_token: str) -> dict:
        """Re-exchange a (long-lived) user token to rotate it."""
        try:
            return self.get_long_lived_token(access_token)
        except Exception as e:
            raise PlatformAPIError(f"Failed to refresh user token: {str(e)}")
    
    def process_post_comments(self, post_id: str):
        """
        Process all comments for an Instagram post
        
        Args:
            post_id: Instagram post ID
        
        Returns:
            list: Processing results
        """
        try:
            comments = self.fetch_comments(post_id)
            results = []
            
            for comment in comments:
                result = self.core_service.process_comment(
                    comment_text=comment.get('text', ''),
                    platform='instagram',
                    external_id=comment.get('id', ''),
                    post_id=post_id
                )
                results.append(result)
            
            return results
        except Exception as e:
            raise PlatformAPIError(f"Failed to process Instagram post comments: {str(e)}")
