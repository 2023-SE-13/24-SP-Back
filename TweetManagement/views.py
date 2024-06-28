import json
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from TweetManagement.models import Tweet
from TweetManagement.serializers import TweetSerializer
from shared.decorators import require_user, require_company


class TweetCURDViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

