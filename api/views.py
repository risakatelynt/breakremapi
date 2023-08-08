from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserProfileSerializer, ReminderSerializer, ThemeSerializer, SettingSerializer
from .models import Reminder, Theme, UserProfile, Setting
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from rest_framework.views import APIView

import os
from django.conf import settings
from .utils import register, user_login, user_logout, getRemindersList, createReminder, updateReminder, deleteReminder, deleteReminders, set_theme, get_theme, set_settings, get_settings


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @api_view(['POST'])
    def register_user(request):
        if request.method == 'POST':
            return register(request)

    @api_view(['POST'])
    def login_user(request):
        if request.method == 'POST':
            return user_login(request)

    @api_view(['POST'])
    def logout_user(request):
        if request.method == 'POST':
            return user_logout(request)


class RemindersViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @api_view(['GET', 'POST'])
    def getReminders(request):
        if request.method == 'GET':
            return getRemindersList(request)

        if request.method == 'POST':
            return createReminder(request)

    @api_view(['PUT', 'DELETE'])
    def getReminder(request, pk):
        # if request.method == 'GET':
        #     return getReminderDetail(request, pk)

        if request.method == 'PUT':
            return updateReminder(request, pk)

        if request.method == 'DELETE':
            return deleteReminder(request, pk)

    @api_view(['POST'])
    def deleteReminders(request):
        if request.method == 'POST':
            return deleteReminders(request)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @api_view(['GET', 'POST'])
    def Themes(request):
        if request.method == 'GET':
            return get_theme(request)

        if request.method == 'POST':
            return set_theme(request)


class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        user = request.user
        file_serializer = None  # Initialize file_serializer
        try:
            user_profile = UserProfile.objects.get(user=user)

            # Delete the existing profile_picture if it exists
            if user_profile.profile_picture:
                file_path = os.path.join(
                    settings.MEDIA_ROOT, user_profile.profile_picture.name)
                os.remove(file_path)

            # If the user profile already exists, update the profile_picture
            user_profile.profile_picture = request.data['profile_picture']
            user_profile.save()

            # Update User model fields (username and email)
            user.username = request.data['username']
            user.email = request.data['email']
            user.save()

            file_serializer = UserProfileSerializer(user_profile)
            # Pass the full URL for the profile_picture field to the frontend
            file_serializer.data['profile_picture'] = request.build_absolute_uri(
                user_profile.profile_picture.url)
            if file_serializer:
                return Response({'resp': 'success', 'message': 'Image uploaded succesfully.', 'data': file_serializer.data['profile_picture']}, status=status.HTTP_201_CREATED)
            else:
                return Response({'resp': 'failed', 'message': 'Image upload failed.'}, status=status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:

            # If the user profile does not exist, create a new one
            file_serializer = UserProfileSerializer(
                data=request.data, context={'user': user})

            if file_serializer.is_valid():
                file_serializer.save()

                # Update User model fields (username and email)
                user.username = request.data['username']
                user.email = request.data['email']
                user.save()

                return Response({'resp': 'success', 'message': 'Image uploaded succesfully.', 'data': file_serializer.data['profile_picture']}, status=status.HTTP_201_CREATED)
            else:
                return Response({'resp': 'failed', 'message': 'Image upload failed.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'resp': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SetUserProfile(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        file_serializer = None  # Initialize file_serializer
        try:
            # Check if the new username or email already exists
            new_username = request.data.get('username')
            new_email = request.data.get('email')

            existing_username = User.objects.filter(
                username=new_username).exclude(pk=user.pk).exists()
            existing_email = User.objects.filter(
                email=new_email).exclude(pk=user.pk).exists()

            if existing_username:
                return Response({'resp': 'failed', 'message': 'Username already exists. Please enter a different username.'})

            if existing_email:
                return Response({'resp': 'failed', 'message': 'Email already exists. Please enter a different email.'})

            user_profile = UserProfile.objects.get(user=user)
            user_profile.save()
            file_serializer = UserProfileSerializer(user_profile)

            if file_serializer:

                # Update User model fields (username and email)
                user.username = request.data['username']
                user.email = request.data['email']
                user.save()

                return Response({'resp': 'success', 'message': 'Updated succesfully.'})
            else:
                return Response({'resp': 'failed', 'message': 'Update failed.'})

        except UserProfile.DoesNotExist:
            try:
                # Check if the new username or email already exists
                new_username = request.data.get('username')
                new_email = request.data.get('email')

                existing_username = User.objects.filter(
                    username=new_username).exclude(pk=user.pk).exists()
                existing_email = User.objects.filter(
                    email=new_email).exclude(pk=user.pk).exists()

                if existing_username:
                    return Response({'resp': 'failed', 'message': 'Username already exists. Please enter a different username.'})

                if existing_email:
                    return Response({'resp': 'failed', 'message': 'Email already exists. Please enter a different email.'})

                # If the user profile does not exist, create a new one
                file_serializer = UserProfileSerializer(
                    data=request.data, context={'user': user})

                if file_serializer.is_valid():
                    file_serializer.save()

                    # Update User model fields (username and email)
                    user.username = request.data['username']
                    user.email = request.data['email']
                    user.save()
                    return Response({'resp': 'success', 'message': 'Updated succesfully.'})
                else:
                    return Response({'resp': 'failed', 'message': 'Update failed.'})
            except Exception as e:
                return Response({'resp': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            serializer = UserProfileSerializer(user_profile)
            if user_profile.profile_picture:
                # Pass the full URL for the profile_picture field to the frontend
                serializer.data['profile_picture'] = request.build_absolute_uri(
                    user_profile.profile_picture.url)
            else:
                # If there is no profile_picture, send a custom message to the frontend
                serializer.data['profile_picture'] = None

            return Response({'resp': 'success', 'data': {'username': user.username,
                                                         'email': user.email, 'profile_picture': serializer.data['profile_picture']}})
        except UserProfile.DoesNotExist:
            return Response({'resp': 'failed', 'message': 'No profile found for the current user.'})
        except Exception as e:
            return Response({'resp': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SettingsViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @api_view(['GET', 'POST'])
    def Settings(request):
        if request.method == 'GET':
            return get_settings(request)

        if request.method == 'POST':
            return set_settings(request)
