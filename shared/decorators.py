from functools import wraps

from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status

from CompanyManagement.models import Company
from PositionManagement.models import Position
from TweetManagement.models import Tweet, Comment
from UserManagement.models import *


def require_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        username = request.GET.get('username')
        if not username:
            username = request.data.get('username')

        email = request.GET.get('email')
        if not email:
            email = request.data.get('email')

        query = Q()
        if username:
            query |= Q(username=username)
        if email:
            query |= Q(email=email)

        if not query:
            return JsonResponse({"status": "error", "message": "Parameter is required"},
                                status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(query).exists():
            return JsonResponse({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(query)
        request.user_object = user  # Attach user to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_company(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        company_id = request.GET.get('company_id')
        if not company_id:
            company_id = request.data.get('company_id')

        if not company_id:
            return JsonResponse({'status': 'error', 'message': 'Missing company_id parameter'}, status=400)

        try:
            company = Company.objects.get(company_id=company_id)
        except Company.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Company does not exist'}, status=404)

        request.company_object = company  # Attach company to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_position(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        position_id = request.GET.get('position_id')
        if not position_id:
            position_id = request.data.get('position_id')

        if not position_id:
            return JsonResponse({'status': 'error', 'message': 'Missing position_id parameter'}, status=400)

        try:
            position = Position.objects.get(position_id=position_id)
        except Position.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Position does not exist'}, status=404)

        request.position_object = position  # Attach position to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def require_tweet(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        tweet_id = request.GET.get('tweet_id')
        if not tweet_id:
            tweet_id = request.data.get('tweet_id')

        if not tweet_id:
            return JsonResponse({'status': 'error', 'message': 'Missing tweet_id parameter'}, status=400)

        try:
            tweet = Tweet.objects.get(tweet_id=tweet_id)
        except Tweet.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tweet does not exist'}, status=404)

        request.tweet_object = tweet  # Attach tweet to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def require_comment(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        comment_id = request.GET.get('comment_id')
        if not comment_id:
            comment_id = request.data.get('comment_id')

        if not comment_id:
            return JsonResponse({'status': 'error', 'message': 'Missing comment_id parameter'}, status=400)

        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Comment does not exist'}, status=404)

        request.comment_object = comment  # Attach comment to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def require_textcontent(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        text_content = request.GET.get('text_content')
        if not text_content:
            text_content = request.data.get('text_content')

        if not text_content:
            return JsonResponse({'status': 'error', 'message': 'Missing content parameter'}, status=400)


        request.text_content = text_content  # Attach comment to request object so that it's available in the view
        return view_func(request, *args, **kwargs)

    return _wrapped_view