from celery import shared_task
from django.utils import timezone
from platforms.instagram.models import InstagramAccount
from platforms.instagram.services import InstagramService
from shopify_integration.models import JudgeReview, ShopifyStore
from shopify_integration.nanobanan import NanobananService
from core.models import InstagramPost
from shared.exceptions import PlatformAPIError


@shared_task
def process_review_to_instagram(review_id):
    """
    Main task: Review → Image → Instagram Post
    
    Args:
        review_id: ID of the JudgeReview to process
    """
    try:
        # 1. Get review from database
        review = JudgeReview.objects.get(id=review_id)
        store = review.shopify_store
        
        # 2. Get Instagram account for this store
        try:
            instagram_account = InstagramAccount.objects.get(user=store.user)
        except InstagramAccount.DoesNotExist:
            raise PlatformAPIError(f"No Instagram account found for user {store.user.username}")
        
        # 3. Create InstagramPost record
        instagram_post = InstagramPost.objects.create(
            user=store.user,
            instagram_account=instagram_account,
            review_id=review.review_id,
            shopify_store=store,
            image_url='',  # Will be updated after generation
            caption=f"⭐ {review.rating}/5 - {review.title}\n\n{review.body[:100]}{'...' if len(review.body) > 100 else ''}\n\n#{store.store_name.replace(' ', '')} #Review #CustomerLove",
            status='generating'
        )
        
        # 4. Generate image with Nanobanan
        nanobanan = NanobananService()
        image_url = nanobanan.generate_review_image(
            review_data={
                'rating': review.rating,
                'title': review.title,
                'body': review.body,
                'reviewer_name': review.reviewer_name
            },
            branding={
                'logo_url': store.logo_url,
                'primary_color': store.primary_color,
                'store_name': store.store_name
            }
        )
        
        # Update InstagramPost with image URL
        instagram_post.image_url = image_url
        instagram_post.status = 'posting'
        instagram_post.save()
        
        # 5. Create Instagram post
        instagram_service = InstagramService()
        instagram_service.bind_access_token(instagram_account.access_token)
        
        # Create container
        container_id = instagram_service.create_container(
            instagram_account.instagram_user_id,
            image_url,
            instagram_post.caption
        )
        
        # Publish container
        media_id = instagram_service.publish_container(
            instagram_account.instagram_user_id,
            container_id
        )
        
        # 6. Update InstagramPost record
        instagram_post.instagram_media_id = media_id
        instagram_post.instagram_permalink = f"https://www.instagram.com/p/{media_id}/"
        instagram_post.status = 'completed'
        instagram_post.posted_at = timezone.now()
        instagram_post.save()
        
        # 7. Mark review as processed
        review.processed = True
        review.save()
        
        return {
            'success': True,
            'instagram_post_id': instagram_post.id,
            'media_id': media_id,
            'image_url': image_url
        }
        
    except JudgeReview.DoesNotExist:
        return {
            'success': False,
            'error': f'Review {review_id} not found'
        }
    except InstagramAccount.DoesNotExist:
        return {
            'success': False,
            'error': f'No Instagram account found for user'
        }
    except PlatformAPIError as e:
        # Update InstagramPost with error
        try:
            instagram_post = InstagramPost.objects.get(review_id=review.review_id)
            instagram_post.status = 'failed'
            instagram_post.error_message = str(e)
            instagram_post.save()
        except InstagramPost.DoesNotExist:
            pass
        
        return {
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        # Update InstagramPost with error
        try:
            instagram_post = InstagramPost.objects.get(review_id=review.review_id)
            instagram_post.status = 'failed'
            instagram_post.error_message = str(e)
            instagram_post.save()
        except InstagramPost.DoesNotExist:
            pass
        
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }



