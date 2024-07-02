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
        guest_recommends = get_guest_recommends()
        return JsonResponse({"status": "success", "data": guest_recommends}, status=200)

    user_recommends = get_user_recommends(request.user)
    return JsonResponse({"status": "success", "data": user_recommends}, status=200)


def get_guest_recommends():
    guest_recommends = {
        "users": [],
        "companies": []
    }
    guest_recommends['users'] = get_guest_hotest_users()
    guest_recommends['companies'] = get_guest_hotest_companies()
    return guest_recommends


def get_guest_hotest_users():
    guest_hotest_users = User.objects.filter().order_by('-user_subscription')[:9]
    guest_users = []
    for user in guest_hotest_users:
        company_name = get_user_company_name(user)
        guest_users.append({
            "username": user.username,
            "avatar": os.path.basename(user.avatar.name) if user.avatar.name else "",
            "company_name": company_name,
        })
    return guest_users


def get_user_company_name(user):
    company_member = CompanyMember.objects.filter(user=user).first()
    return company_member.company.company_name if company_member else ""


def get_guest_hotest_companies():
    guest_hotest_companies = Company.objects.filter().order_by('-company_subscription')[:12]
    guest_companies = []
    for company in guest_hotest_companies:
        guest_companies.append({
            "company_id": company.company_id,
            "company_name": company.company_name,
            "company_image": os.path.basename(company.company_image.name) if company.company_image.name else "",
        })
    return guest_companies


def get_user_recommends(user):
    desired_positions = user.desired_position.all()
    positions = get_related_positions(desired_positions)
    related_users = get_related_users(user)
    related_companies = get_related_companies(positions)

    recommends = {
        "users": [],
        "companies": []
    }
    recommends['users'] = get_recommended_users(user, related_users)
    recommends['companies'] = get_recommended_companies(related_companies)

    return recommends


def get_related_positions(desired_positions):
    return Position.objects.filter(position_tag__in=desired_positions).annotate(
        num_common_position_tag=Count('position_tag')).filter(
        num_common_position_tag__gt=0).order_by('-num_common_position_tag')


def get_related_users(user):
    user_skills = user.skills.all()
    return User.objects.filter(skills__in=user_skills).exclude(username=user.username).annotate(
        num_common_skills=Count('skills')).filter(
        num_common_skills__gt=0).order_by('-num_common_skills')


def get_related_companies(positions):
    related_companies = QuerySet(Company)
    for position in positions:
        related_companies = related_companies.union(
            Company.objects.filter(company_id=position.company.company_id))
    return related_companies


def get_recommended_users(user, related_users):
    if len(related_users) < 6:
        hotest_users = User.objects.filter().annotate(num_common_skills=Count('skills')).order_by(
            '-user_subscription').exclude(username=user.username)[:9]
        related_users = related_users.union(hotest_users)

    recommended_users = []
    for i, related_user in enumerate(related_users):
        if i >= 9:
            break
        company_name = get_user_company_name(related_user)
        recommended_users.append({
            "username": related_user.username,
            "avatar": os.path.basename(related_user.avatar.name) if related_user.avatar.name else "",
            "company_name": company_name,
        })
    return recommended_users


def get_recommended_companies(related_companies):
    if len(related_companies) < 12:
        hotest_companies = Company.objects.filter().order_by('-company_subscription')[:12]
        related_companies = related_companies.union(hotest_companies)

    recommended_companies = []
    for i, related_company in enumerate(related_companies):
        if i >= 12:
            break
        recommended_companies.append({
            "company_id": related_company.company_id,
            "company_name": related_company.company_name,
            "company_image": os.path.basename(
                related_company.company_image.name) if related_company.company_image.name else "",
        })
    return recommended_companies

@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def recommend_position(request):
    if request.user.is_authenticated:
        return get_authenticated_user_recommendations(request.user)
    else:
        return get_guest_recommendations()


def get_authenticated_user_recommendations(user):
    user = User.objects.get(username=user.username)
    recommends = []
    desired_positions = user.desired_position.all()

    if desired_positions:
        related_positions = get_related_positions(desired_positions)
        if len(related_positions) < 6:
            related_positions = add_latest_positions(related_positions)
        recommends = get_position_recommendations(related_positions, 6)
    else:
        latest_positions = get_latest_positions(6)
        recommends = get_position_recommendations(latest_positions, 6)

    return JsonResponse({"status": "success", "data": recommends}, status=200)


def get_guest_recommendations():
    latest_positions = get_latest_positions(6)
    recommends = get_position_recommendations(latest_positions, 6)
    return JsonResponse({"status": "success", "data": recommends}, status=200)


def get_related_positions(desired_positions):
    return Position.objects.filter(position_tag__in=desired_positions).annotate(
        num_common_position_tag=Count('position_tag')).filter(
        num_common_position_tag__gt=0).order_by('-posted_at')


def add_latest_positions(related_positions):
    latest_positions = Position.objects.filter().annotate(
        num_common_position_tag=Count('position_tag')).order_by('-posted_at')[:6]
    return related_positions.union(latest_positions)


def get_latest_positions(limit):
    return Position.objects.filter().order_by('-posted_at')[:limit]


def get_position_recommendations(positions, limit):
    recommends = []
    for i, position in enumerate(positions):
        if i >= limit:
            break
        recommends.append(PositionSerializer(position).data)
    return recommends


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

