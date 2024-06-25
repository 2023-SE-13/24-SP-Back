from functools import wraps

from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status

from CompanyManagement.models import Company
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
