import requests
from django.conf import settings
from shared.exceptions import PlatformAPIError


class NanobananService:
    """Service for generating images using Google Nanobanan API"""
    
    def __init__(self):
        self.api_key = settings.NANOBANAN_API_KEY
        self.base_url = "https://api.nanobanan.com/v1"  # Update with actual API URL
    
    def generate_review_image(self, review_data, branding):
        """
        Generate branded review image
        
        Args:
            review_data: dict with rating, title, body, reviewer_name
            branding: dict with logo_url, primary_color, store_name
            
        Returns:
            str: URL to generated image
        """
        if not self.api_key:
            raise PlatformAPIError("Nanobanan API key not configured")
        
        # Prepare prompt for image generation
        prompt = self._build_image_prompt(review_data, branding)
        
        # Call Nanobanan API
        payload = {
            'prompt': prompt,
            'style': 'review_card',
            'branding': {
                'logo_url': branding.get('logo_url'),
                'primary_color': branding.get('primary_color', '#000000'),
                'store_name': branding.get('store_name', 'Store')
            },
            'dimensions': '1080x1080',  # Instagram square format
            'quality': 'high'
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/images/generate",
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'image_url' in data:
                return data['image_url']
            else:
                raise PlatformAPIError(f"Failed to generate image: {data}")
                
        except requests.Timeout:
            raise PlatformAPIError("Nanobanan API request timed out")
        except requests.RequestException as e:
            raise PlatformAPIError(f"Failed to generate image: {str(e)}")
    
    def _build_image_prompt(self, review_data, branding):
        """Build a detailed prompt for image generation"""
        rating = review_data.get('rating', 0)
        title = review_data.get('title', '')
        body = review_data.get('body', '')
        reviewer_name = review_data.get('reviewer_name', 'Customer')
        store_name = branding.get('store_name', 'Store')
        
        # Create star rating text
        stars = '⭐' * rating + '☆' * (5 - rating)
        
        # Build the prompt
        prompt = f"""
        Create a beautiful Instagram post design for a customer review:
        
        Store: {store_name}
        Product Review: {title}
        Rating: {stars} ({rating}/5)
        Review: "{body[:200]}{'...' if len(body) > 200 else ''}"
        Reviewer: {reviewer_name}
        
        Design requirements:
        - Modern, clean layout suitable for Instagram
        - Use the store's primary color: {branding.get('primary_color', '#000000')}
        - Include the store logo if available
        - Make it visually appealing with good typography
        - Include star rating prominently
        - Professional but friendly tone
        - High contrast for readability
        - Square format (1080x1080)
        """
        
        return prompt.strip()



