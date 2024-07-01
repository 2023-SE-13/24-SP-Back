import os
from django.db.models import Count, QuerySet
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from itertools import chain

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from CompanyManagement.models import Company, CompanyMember
from PositionManagement.models import Position
from PositionManagement.serializer import PositionSerializer
from UserManagement.models import User
from shared.decorators import require_position

# Create your views here.
@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def recommend_subscribe(request):
    if not request.user.is_authenticated:
        guest_recommends = {
            "users": [],
            "companies": []
        }
        guest_hotest_users = User.objects.filter().order_by('-user_subscription')[:6]
        for guest_hotest_user in guest_hotest_users:
            guest_company_member = CompanyMember.objects.filter(user=guest_hotest_user).first()
            guest_company_name = ""
            if guest_company_member:
                guest_company_name = guest_company_member.company.company_name
            guest_recommends['users'].append({
                "username": guest_hotest_user.username,
                "avatar": os.path.basename(guest_hotest_user.avatar.name) if guest_hotest_user.avatar.name else "",
                "company_name": guest_company_name,
            })
        guest_hotest_companies = Company.objects.filter().order_by('-company_subscription')[:6]
        for guest_hotest_company in guest_hotest_companies:
            guest_recommends['companies'].append({
                "company_id": guest_hotest_company.company_id,
                "company_name": guest_hotest_company.company_name,
                "company_image": os.path.basename(
                    guest_hotest_company.company_image.name) if guest_hotest_company.company_image.name else "",
            })
        return JsonResponse({"status": "success", "data": guest_recommends}, status=200)
    # 用户已登录
    user = User.objects.get(username=request.user.username)
    desired_position = user.desired_position.all()
    positions = Position.objects.filter(position_tag__in=desired_position).annotate(num_common_position_tag=Count('position_tag')).filter(num_common_position_tag__gt=0).order_by('-num_common_position_tag')
    user_skills = user.skills.all()
    related_users = User.objects.filter(skills__in=user_skills).exclude(username=user.username).annotate(num_common_skills=Count('skills')).filter(num_common_skills__gt=0).order_by('-num_common_skills')
    related_companies = QuerySet(Company)
    for position in positions:  
        related_companies = related_companies.union(Company.objects.filter(company_id=position.company_id))
    recommends = {
        "users": [],
        "companies": []
    }
    if len(related_users) < 6:
        hotest_users = User.objects.filter().order_by('-user_subscription')[:6]
        related_users = list(chain(hotest_users, related_users))
        
    if len(related_companies) < 6:
        hotest_companies = Company.objects.filter().order_by('-company_subscription')[:6]
        related_companies = list(chain(hotest_companies, related_companies))
    related_users = related_users[:6]
    related_companies = related_companies[:6]
    for related_user in related_users:
        company_member = CompanyMember.objects.filter(user=related_user).first()
        company_name = ""
        if company_member:
            company_name = company_member.company.company_name
        recommends['users'].append({
            "username": related_user.username,
            "avatar": os.path.basename(related_user.avatar.name) if related_user.avatar.name else "",
            "company_name": company_name,
        })
    for related_company in related_companies:
        recommends['companies'].append({
            "company_id": related_company.company_id,
            "company_name": os.path.basename(related_company.company_name) if related_company.company_name else "",
            "company_image": related_company.company_image.name,
        })


    return JsonResponse({"status": "success", "data": recommends}, status=200)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def recommend_position(request):
    if request.user.is_authenticated:
        user = User.objects.get(username =request.user.username)
        recommends = []
        desired_position = user.desired_position.all()
        if desired_position:
            related_positions = Position.objects.filter(position_tag__in=desired_position).annotate(num_common_position_tag=Count('position_tag')).filter(num_common_position_tag__gt=0).order_by('-num_common_position_tag')
            if len(related_positions) < 6:
                latest_positions = Position.objects.filter().order_by('-posted_at')[:6]
                related_positions = list(chain(related_positions, latest_positions))[:6]
            for related_position in related_positions:
                recommends.append(PositionSerializer(related_position).data)
        else:
            latest_positions = Position.objects.filter().order_by('-posted_at')[:6]
            for latest_position in latest_positions:
                recommends.append(PositionSerializer(latest_position).data)
        return JsonResponse({"status": "success", "data": recommends}, status=200)
    else:
        latest_positions = Position.objects.filter().order_by('-posted_at')[:6]
        recommends = []
        for latest_position in latest_positions:
            recommends.append(PositionSerializer(latest_position).data)
        return JsonResponse({"status": "success", "data": recommends}, status=200)


@csrf_exempt
@api_view(['GET'])
@require_position
def recommend_simposition(request):
    position = request.position_object
    recommends = []
    desired_position = position.position_tag
    if desired_position:
        related_positions = Position.objects.filter(position_tag=desired_position).annotate(num_common_position_tag=Count('position_tag')).filter(num_common_position_tag__gt=0).exclude(position_id=position.position_id).order_by('-num_common_position_tag')

        for related_position in related_positions:
            recommends.append(PositionSerializer(related_position).data)
    else:
        latest_positions = Position.objects.filter().order_by('-posted_at')[:9]
        for latest_position in latest_positions:
            recommends.append(PositionSerializer(latest_position).data)
    return JsonResponse({"status": "success", "data": recommends}, status=200)

