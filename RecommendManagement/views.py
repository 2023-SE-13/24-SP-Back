from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from CompanyManagement.models import Company
from PositionManagement.models import Position
from PositionManagement.serializer import PositionSerializer
from UserManagement.models import User


# Create your views here.
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def recommend_subscribe(request):
    user = request.user
    desired_position = user.desired_position
    positions = Position.objects.filter(position_tag=desired_position)
    user_skills = user.skills.all()
    related_users = User.objects.filter(skills__in=user_skills).exclude(username=user.username).annotate(num_common_skills=Count('skills')).filter(num_common_skills__gt=0).order_by('-num_common_skills')
    related_companies = []
    for position in positions:  
        related_companies.append(position.company.company_id)
    recommends = {
        "users": [],
        "companies": []
    }
    for related_user in related_users:
        recommends['users'].append({
            "username": related_user.username,
        })
    for related_company in related_companies:
        company = Company.objects.get(company_id=related_company)
        recommends['companies'].append({
            "company_name": company.company_name,
        })
    return JsonResponse({"status": "success", "data": recommends}, status=200)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def recommend_position(request):
    user = request.user
    related_positions = Position.objects.filter(position_tag=user.desired_position)
    recommends = []
    for related_position in related_positions:
        recommends.append(PositionSerializer(related_position).data)
    return JsonResponse({"status": "success", "data": recommends}, status=200)


