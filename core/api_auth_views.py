from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework import serializers

from shared.api_responses import success_response, error_response


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        if not username and not email:
            raise serializers.ValidationError('Provide either username or email')
        if not password:
            raise serializers.ValidationError('Password is required')
        return attrs


class LoginView(APIView):
    # Explicitly disable default authentication (Token/Session) to avoid CSRF on POST
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message='Invalid credentials',
                code='VALIDATION_ERROR',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data['password']

        if email and not username:
            try:
                user_obj = User.objects.get(email__iexact=email)
                username = user_obj.username
            except User.DoesNotExist:
                return error_response(
                    message='Invalid username/email or password',
                    code='AUTH_FAILED',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

        user = authenticate(request, username=username, password=password)
        if not user:
            return error_response(
                message='Invalid username/email or password',
                code='AUTH_FAILED',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return success_response(
            data={
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            },
            message='Login successful',
            status_code=status.HTTP_200_OK,
        )


class MeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return success_response(
            data={
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            message='Current user',
            status_code=status.HTTP_200_OK,
        )



