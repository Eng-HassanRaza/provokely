"""
Abstract interfaces for platform services
"""
from abc import ABC, abstractmethod


class PlatformServiceInterface(ABC):
    """Interface for platform-specific services"""
    
    @abstractmethod
    def fetch_posts(self, account_id: str, limit: int = 10):
        """Fetch posts from platform"""
        pass
    
    @abstractmethod
    def fetch_comments(self, post_id: str):
        """Fetch comments for a specific post"""
        pass
    
    @abstractmethod
    def post_comment(self, post_id: str, text: str):
        """Post a comment to a specific post"""
        pass
    
    @abstractmethod
    def authenticate(self, credentials: dict):
        """Authenticate with platform"""
        pass


class SentimentAnalyzerInterface(ABC):
    """Interface for sentiment analysis"""
    
    @abstractmethod
    def analyze(self, text: str) -> dict:
        """Analyze sentiment of text"""
        pass
    
    @abstractmethod
    def batch_analyze(self, texts: list) -> list:
        """Analyze sentiment for multiple texts"""
        pass


class ResponseGeneratorInterface(ABC):
    """Interface for AI response generation"""
    
    @abstractmethod
    def generate(self, sentiment: dict, platform: str, comment_text: str = None) -> str:
        """Generate AI response based on sentiment"""
        pass
