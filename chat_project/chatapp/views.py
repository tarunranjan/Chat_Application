from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, Message
from .serializers import UserSerializer, UserProfileSerializer
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
import json
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            UserProfile.objects.create(user=user)
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.online = True
            user_profile.save()
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_online_users(request):
    # Get a list of online users
    online_users = UserProfile.objects.filter(online=True)
    serializer = UserProfileSerializer(online_users, many=True)
    return Response({'online_users': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat(request):
    recipient_id = request.data.get('recipient_id')
    print(recipient_id)
    try:
        recipient = UserProfile.objects.get(user_id=recipient_id, online=True)
        print(recipient)
        return Response({'message': 'Chat started successfully'}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Recipient is offline or not found'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    sender = request.user
    recipient_id = request.data.get('recipient_id')
    message_content = request.data.get('message_content')
    
    try:
        # Checking recipient is online or not
        recipient = UserProfile.objects.get(user_id=recipient_id, online=True)
        
        # Creating a Message object
        message = Message.objects.create(sender=sender, receiver=recipient.user, content=message_content)
        
        
        return Response({'message': 'Message sent successfully'}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Recipient is offline or not found'}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

@api_view(['GET'])
def suggested_friends(request, user_id):
    # Load the JSON data for friend recommendations
    with open('users.json') as json_file:
        data = json.load(json_file)
    
    user_data = None
    for user in data["users"]:
        if user['id'] == int(user_id):  
            user_data = user
            break
    
    if not user_data:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    suggested_friends = []
    for other_user in data["users"]:
        if other_user['id'] != user_data['id']:
            common_interests = set(user_data['interests'].keys()) & set(other_user['interests'].keys())
            if common_interests:
                suggested_friends.append(other_user)
                if len(suggested_friends) >= 5:
                    break
    
    return Response({'suggested_friends': suggested_friends}, status=status.HTTP_200_OK)
