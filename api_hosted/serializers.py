from rest_framework import serializers


class AuthRequestSerializer(serializers.Serializer):
    """Serializer for authentication request"""
    email = serializers.EmailField(required=True)


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication response"""
    authToken = serializers.CharField()
    userId = serializers.CharField()
    message = serializers.CharField()


class AIRequestSerializer(serializers.Serializer):
    """Serializer for AI proxy request"""
    prompt = serializers.CharField(required=True)
    userEmail = serializers.EmailField(required=True)
    options = serializers.DictField(required=False, default=dict)
    
    def validate_options(self, value):
        """Validate options field"""
        if value is None:
            return {}
        return value


class AIResponseSerializer(serializers.Serializer):
    """Serializer for AI proxy response"""
    response = serializers.CharField()
    tokensUsed = serializers.IntegerField()
    cost = serializers.FloatField()

