from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from core.models import UserSettings
from core.serializers import UserSettingsSerializer
from shared.api_responses import success_response, error_response


class InstagramSettingsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            settings = UserSettings.objects.get(user=request.user)
        except UserSettings.DoesNotExist:
            settings = UserSettings.objects.create(user=request.user)
        serializer = UserSettingsSerializer(settings)
        return success_response(serializer.data, 'Instagram settings fetched')

    def put(self, request):
        try:
            settings = UserSettings.objects.get(user=request.user)
        except UserSettings.DoesNotExist:
            settings = UserSettings.objects.create(user=request.user)
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response('Validation failed', details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return success_response(serializer.data, 'Instagram settings updated')



