"""
AI Response Generation Module
Platform-agnostic response generation based on sentiment analysis
"""


from django.conf import settings
try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


class ResponseGenerator:
    """
    Generates AI-driven responses based on comment sentiment
    This is a placeholder implementation - will be enhanced with actual AI models
    """
    
    def __init__(self):
        # Default response templates
        self.response_templates = {
            'positive': [
                "Thank you for your positive feedback! 😊",
                "We're so glad you enjoyed it! ❤️",
                "Your support means everything to us! 🙏",
            ],
            'negative': [
                "We appreciate your feedback and will work to improve.",
                "Thank you for sharing your concerns. We're here to help!",
                "We're sorry to hear that. Please let us know how we can make it better.",
            ],
            'neutral': [
                "Thanks for sharing your thoughts!",
                "We appreciate your comment!",
                "Thank you for engaging with us!",
            ],
            'hate': [
                "Interesting perspective! 🤔 What made you feel this way?",
                "Wow, that's quite the opinion! 😅 Care to elaborate?",
                "Hmm, someone woke up on the wrong side of the bed today! 😂",
                "That's... creative! 🎨 Tell me more about your thought process.",
                "Oh my, such strong feelings! 💪 What's the real story here?",
            ]
        }
    
    def generate(self, sentiment: dict, platform: str, comment_text: str = None) -> str:
        """
        Generate AI response based on sentiment
        
        Args:
            sentiment: Sentiment analysis result
            platform: Platform name
            comment_text: Original comment text (optional, for context)
        
        Returns:
            str: Generated response
        """
        label = sentiment.get('label', 'neutral')
        nuanced = sentiment.get('nuanced_label')
        # If OpenAI is configured, generate with prompt rules
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        if OpenAI and api_key and comment_text:
            try:
                client = OpenAI(api_key=api_key)
                system = (
                    "You craft ultra-short, high-impact replies for Instagram comments to maximize engagement.\n"
                    "Constraints:\n"
                    "- Output only the reply. No preamble.\n"
                    "- Max 18 words.\n"
                    "- No slurs, no harassment, no threats, PG-13, platform-safe.\n"
                    "Styles by sentiment:\n"
                    "- positive: ultra-short, warm, human, include ❤ or similar.\n"
                    "- negative/hate: human, edgy clapback, slightly contemptuous but safe; ‘revenge energy’ without harassment;\n"
                    "  vary form (mostly statements; occasional short tag-question).\n"
                )
                style_hint = ''
                if label == 'positive':
                    style_hint = 'Style: short, warm, appreciative with ❤.'
                elif label in ['hate', 'negative']:
                    style_hint = 'Style: edgy clapback, witty roast, human and safe; prefer statements; end without a question unless it’s a short tag.'
                else:
                    style_hint = 'Style: concise, friendly.'
                user = (
                    f"Original comment (reply in same language): {comment_text}\n"
                    f"Primary: {label}\nNuanced: {nuanced or 'none'}\n"
                    f"{style_hint}"
                )
                comp = client.chat.completions.create(
                    model=model,
                    temperature=0.7,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                reply = (comp.choices[0].message.content or '').strip()
                # Enforce max 18 words
                words = reply.split()
                if len(words) > 18:
                    reply = ' '.join(words[:18])
                # Safety: cap to 140 chars
                return reply[:140]
            except Exception:
                pass
        # Fallback to template
        templates = self.response_templates.get(label, self.response_templates['neutral'])
        return templates[0]
    
    def generate_with_context(self, sentiment: dict, platform: str, comment_text: str, 
                              post_content: str = None, user_history: list = None) -> str:
        """
        Generate context-aware AI response
        
        Args:
            sentiment: Sentiment analysis result
            platform: Platform name
            comment_text: Original comment text
            post_content: Original post content (optional)
            user_history: User's comment history (optional)
        
        Returns:
            str: Generated contextual response
        """
        # TODO: Implement context-aware response generation with AI
        # This would use the post content and user history to generate more relevant responses
        
        return self.generate(sentiment, platform, comment_text)
    
    def customize_templates(self, templates: dict):
        """
        Customize response templates
        
        Args:
            templates: Dictionary of templates by sentiment label
        """
        self.response_templates.update(templates)
