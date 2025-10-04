"""
Sentiment Analysis Module
Platform-agnostic sentiment analysis for social media comments
"""

from typing import Optional, List
import json
from django.conf import settings
import logging

try:
    # OpenAI Python SDK (>=1.0)
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore
try:
    # Legacy OpenAI SDK (<1.0)
    import openai  # type: ignore
except Exception:
    openai = None  # type: ignore

logger = logging.getLogger("provokely")

class SentimentAnalyzer:
    """
    GPT-powered sentiment analysis with graceful fallback.
    Returns labels in {'positive','negative','neutral','hate'} with score (-1..1) and confidence (0..1).
    """
    
    def __init__(self):
        self._client = None
        self._model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self._use_legacy = False
        if OpenAI and api_key:
            try:
                self._client = OpenAI(api_key=api_key)
                logger.info("SentimentAnalyzer: OpenAI client initialized (model=%s)", self._model)
            except Exception:
                self._client = None
                logger.exception("SentimentAnalyzer: Failed to initialize OpenAI client")
        elif openai and api_key:
            try:
                openai.api_key = api_key
                self._use_legacy = True
                self._client = openai
                logger.info("SentimentAnalyzer: Legacy OpenAI client initialized (model=%s)", self._model)
            except Exception:
                self._client = None
                logger.exception("SentimentAnalyzer: Failed to initialize legacy OpenAI client")
        # Fallback thresholds for rule-based backup
        self.positive_threshold = 0.6
        self.negative_threshold = 0.4
    
    def analyze(self, text: str) -> dict:
        if self._client and text:
            try:
                return self._classify_with_gpt(text)
            except Exception:
                # Fall back on failure
                logger.exception("SentimentAnalyzer: GPT classify failed, using fallback")
        return self._fallback_rule_based(text)
    
    def batch_analyze(self, texts: List[str]) -> List[dict]:
        # Simple per-item calls to keep logic straightforward for now
        return [self.analyze(t) for t in texts]

    # ---------------- Internal helpers ----------------
    def _classify_with_gpt(self, text: str) -> dict:
        # User-provided prompt specification (exact)
        system_prompt = (
            "You are an expert multilingual sentiment analysis system.  \n"
            "Your task is to analyze each given comment and produce a structured JSON output.  \n\n"
            "### Steps you must follow for every comment:\n"
            "1. **Detect the exact language** of the comment (e.g., English, Spanish, Roman Urdu, Arabic, German, etc.).  \n"
            "2. **Translate the comment into English** for clarity (without changing the meaning).  \n"
            "3. **Determine the sentiment and intent**.  \n"
            "4. Classify the comment into exactly one of the following categories:\n"
            "   - Positive (praise, appreciation, love, excitement, compliment)  \n"
            "   - Negative (criticism, disapproval, mocking, disappointment)  \n"
            "   - Neutral (informative, casual, unclear tone, unrelated)  \n"
            "   - Hate / Offensive (toxic, abusive, hateful, discriminatory)  \n"
            "   - Purchase Intent (interest in buying, asking price, showing willingness to purchase)  \n"
            "   - Question / Clarification (asking for more details, e.g., \"where can I buy?\", \"how did you do this?\")  \n\n"
            "### Output format (strict JSON):\n"
            "{\n"
            "  \"language\": \"<detected language>\",\n"
            "  \"translated_text\": \"<English translation of comment>\",\n"
            "  \"category\": \"<one of the categories>\",\n"
            "  \"explanation\": \"<brief reasoning in 1-2 sentences>\"\n"
            "}\n\n"
            "### Example\n\n"
            "Input Comment: \"Is sy achi to main bna lyta\"\n\n"
            "Output:\n"
            "{\n"
            "  \"language\": \"Roman Urdu\",\n"
            "  \"translated_text\": \"I could have made a better one than this\",\n"
            "  \"category\": \"Negative\",\n"
            "  \"explanation\": \"The comment criticizes the post by claiming the user could create something better.\"\n"
            "}\n\n"
            "Now analyze the following comment(s):\n"
        )
        user_prompt = f"{text}"
        # Use chat.completions with JSON-style response
        logger.debug("SentimentAnalyzer: Calling GPT sentiment (model=%s, legacy=%s)", self._model, self._use_legacy)
        if self._use_legacy:
            completion = self._client.ChatCompletion.create(  # type: ignore[attr-defined]
                model=self._model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = completion['choices'][0]['message']['content'] or "{}"
        else:
            completion = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = completion.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            category = str(data.get('category', 'Neutral')).strip()
            language = str(data.get('language', '')).strip()
            translated = str(data.get('translated_text', '')).strip()
            explanation = str(data.get('explanation', '')).strip()

            # Map category -> internal primary label and nuanced intent
            cat_lower = category.lower()
            if 'hate' in cat_lower or 'offensive' in cat_lower:
                label = 'hate'
                nuanced = 'none'
            elif 'positive' in cat_lower:
                label = 'positive'
                nuanced = 'appreciation'
            elif 'negative' in cat_lower:
                label = 'negative'
                nuanced = 'complaint'
            elif 'purchase' in cat_lower:
                label = 'neutral'
                nuanced = 'buying_desire'
            elif 'question' in cat_lower:
                label = 'neutral'
                nuanced = 'question'
            else:
                label = 'neutral'
                nuanced = 'none'

            # Confidence/score not provided; use defaults
            return {
                'score': 0.0,
                'label': label,
                'nuanced_label': nuanced,
                'confidence': 0.9,
                'language': language,
                'translated_text': translated,
                'category': category,
                'explanation': explanation,
            }
        except Exception:
            logger.exception("SentimentAnalyzer: Failed to parse GPT sentiment JSON")
            return self._fallback_rule_based(text)

    def _fallback_rule_based(self, text: str) -> dict:
        text_lower = (text or '').lower()
        positive_words = ['love', 'great', 'awesome', 'excellent', 'amazing', 'best', 'wonderful', 'fantastic', 'good', 'nice', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'horrible', 'poor', 'disappointing', 'useless', 'waste']
        hate_words = ['hate', 'stupid', 'idiot', 'moron', 'dumb', 'ugly', 'disgusting', 'pathetic', 'loser', 'trash', 'garbage', 'kill', 'die']
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        hate_count = sum(1 for w in hate_words if w in text_lower)
        nuanced = 'none'
        # Heuristics for nuanced intent
        if any(k in text_lower for k in ['love', '❤', '😍']):
            nuanced = 'love'
        elif any(k in text_lower for k in ['thanks', 'thank you', 'appreciate']):
            nuanced = 'appreciation'
        elif any(k in text_lower for k in ['buy', 'purchase', 'price', 'how much', 'order']):
            nuanced = 'buying_desire'
        elif any(k in text_lower for k in ['more like this', 'more of this', 'do more', 'another one']):
            nuanced = 'more_like_this_desire'
        elif any(k in text_lower for k in ["won't", 'will not', 'never', "don't", 'nope']):
            nuanced = 'resist'
        elif any(k in text_lower for k in ['wtf', 'trash', 'scam', 'refund', 'broken']):
            nuanced = 'complaint'
        elif any(k in text_lower for k in ['?', 'how', 'what', 'when', 'where', 'why']):
            nuanced = 'question'

        if hate_count > 0:
            return {'score': -0.9, 'label': 'hate', 'nuanced_label': 'none', 'confidence': 0.95}
        if positive_count > negative_count:
            return {'score': 0.7, 'label': 'positive', 'nuanced_label': nuanced, 'confidence': 0.85}
        if negative_count > positive_count:
            return {'score': -0.7, 'label': 'negative', 'nuanced_label': nuanced, 'confidence': 0.85}
        return {'score': 0.0, 'label': 'neutral', 'nuanced_label': nuanced, 'confidence': 0.75}
