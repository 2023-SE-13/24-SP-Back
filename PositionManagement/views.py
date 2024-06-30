import json

import pytz
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from CompanyManagement.models import CompanyMember
from NotificationCenter.models import Notification
from NotificationCenter.views.utils.notifications import create_notification
from PositionManagement.models import Position, Application, Offer
from NotificationCenter.views.utils.notifications import create_notification
from PositionManagement.models import Position, Application
from PositionManagement.serializer import PositionSerializer
from Subscribe.models import SubscribeCompany, SubscribeUser
from UserManagement.models import User, Skill, PositionTag
from shared.decorators import require_position, require_company


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_position(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    cm = CompanyMember.objects.filter(user=cur_user).first()
    if cm is None:
        return JsonResponse({"status": "error", "message": "You are not a member of any company"},
                            status=status.HTTP_400_BAD_REQUEST)
    if cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to create position"},
                            status=status.HTTP_400_BAD_REQUEST)
    company = cm.company
    position_name = data.get('position_name')
    position_description = data.get('position_description')
    location = data.get('location')
    education_requirement = data.get('education_requirement')
    salary_min = data.get('salary_min')
    salary_max = data.get('salary_max')
    skill_required = data.get('skill_required')
    if data.get('position_tag'):
        position_tag = PositionTag.objects.filter(category=data.get('position_tag').get('category'),
                                              specialization=data.get('position_tag').get('specialization')).first()
    else:
        position_tag = None
    if not position_name or not position_description:
        return JsonResponse(
            {"status": "error", "message": "position_name, position_description are required"},
            status=status.HTTP_406_NOT_ACCEPTABLE)
    position = Position(company=company, position_name=position_name, position_description=position_description,
                        location=location, education_requirement=education_requirement, salary_min=salary_min,
                        salary_max=salary_max, hr=cur_user, position_tag=position_tag)
    position.save()
    for skill in skill_required:
        position.skill_required.add(Skill.objects.get(name=skill))
    position.save()
    # 向关注该用户所属公司的所有用户推送通知

    company_subscriber = SubscribeCompany.objects.filter(company=company)
    for subscriber in company_subscriber:
        create_notification(json.dumps({
            "username": subscriber.user.username,
            "notification_type": "subscribe",
            "content": f"Company {company.company_name} has created a new position",
            "position_id": str(position.position_id)
        }))

    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@require_position
def get_position(request):
    position = request.position_object
    serializer = PositionSerializer(position)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_position(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    cm = CompanyMember.objects.filter(user=cur_user).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to update position"},
                            status=status.HTTP_400_BAD_REQUEST)
    position = Position.objects.filter(position_id=data.get('position_id')).first()
    if position is None or position.company != cm.company:
        return JsonResponse({"status": "error", "message": "You are not allowed to update position"},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        fields_to_update = ['position_name', 'position_description', 'location', 'education_requirement']
        for field in fields_to_update:
            if data.get(field):
                setattr(position, field, data.get(field))
        skill_required = data.get('skill_required')
        if skill_required:
            position.skill_required.clear()
            for skill in skill_required:
                position.skill_required.add(Skill.objects.get(name=skill))
        position.save()
        return JsonResponse({"status": "success", "message": "Position updated successfully"},
                            status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_position
def delete_position(request):
    position = request.position_object
    cur_user = request.user
    cm = CompanyMember.objects.filter(user=cur_user).first()
    if cm is None:
        return JsonResponse({"status": "error", "message": "You are not a member of any company"},
                            status=status.HTTP_400_BAD_REQUEST)
    if cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to delete position"},
                            status=status.HTTP_400_BAD_REQUEST)
    position.delete()
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@require_company
def get_position_list(request):
    company = request.company_object
    positions = Position.objects.filter(company=company)
    serializer = PositionSerializer(positions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_position
def apply_position(request):
    cur_usr = request.user
    position = request.position_object
    if Application.objects.filter(user=cur_usr, position=position).exists():
        return JsonResponse({"status": "error", "message": "You have already applied for this position"},
                            status=status.HTTP_400_BAD_REQUEST)
    if cur_usr.is_staff:
        return JsonResponse({"status": "error", "message": "Staff cannot apply for position"},
                            status=status.HTTP_400_BAD_REQUEST)
    if User.objects.get(username=cur_usr.username).resume is None:
        return JsonResponse({"status": "error", "message": "Please upload your resume before applying for a position"},
                            status=status.HTTP_400_BAD_REQUEST)
    tz = pytz.timezone('Asia/Shanghai')
    utc8time = timezone.now().astimezone(tz)
    application = Application(user=cur_usr, position=position, applied_at=utc8time)
    application.save()
    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@require_position
def get_position_applications(request):
    cur_user = request.user
    position = request.position_object
    company = position.company
    cm = CompanyMember.objects.filter(user=cur_user, company=company).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to view applications"},
                            status=status.HTTP_400_BAD_REQUEST)
    applications = Application.objects.filter(position__position_id=position.position_id)
    result = []
    for application in applications:
        result.append({
            'application_id': application.application_id,
            'username': application.user.username,
            'real_name': application.user.real_name,
            'education': application.user.education,
            'skills': [skill.name for skill in application.user.skills.all()],
            'applied_at': application.applied_at,
        })
    return JsonResponse(result, status=status.HTTP_200_OK, safe=False)


@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def refuse_application(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    application = Application.objects.filter(application_id=data.get('application_id')).first()
    if application is None:
        return JsonResponse({"status": "error", "message": "Application does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    position = application.position
    company = position.company
    cm = CompanyMember.objects.filter(user=cur_user, company=company).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to refuse application"},
                            status=status.HTTP_400_BAD_REQUEST)
    Application.objects.filter(application_id=application.application_id).delete()
    create_notification({
        "username": application.user.username,
        "notification_type": "system",
        "content": f"Your application for {position.position_name} has been refused by {company.company_name}",
    })
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_offer(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    application = Application.objects.filter(application_id=data.get('application_id')).first()
    if application is None:
        return JsonResponse({"status": "error", "message": "Application does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    position = application.position
    company = position.company
    cm = CompanyMember.objects.filter(user=cur_user, company=company).first()
    if cm is None or cm.role == 'Staff':
        return JsonResponse({"status": "error", "message": "You are not allowed to create offer"},
                            status=status.HTTP_400_BAD_REQUEST)
    if Offer.objects.filter(application=application).exists():
        return JsonResponse({"status": "error", "message": "Offer already exists"},
                            status=status.HTTP_400_BAD_REQUEST)
    offer = Offer(application=application, company=company, receiver=application.user, position=position)
    tz = pytz.timezone('Asia/Shanghai')
    utc8time = timezone.now().astimezone(tz)
    offer.offer_at = utc8time
    offer.save()
    application.offer = offer
    create_notification(json.dumps({
        "username": application.user.username,
        "notification_type": "system",
        "content": f"You have received an offer from {company.company_name} for {position.position_name}",
        "company_id": str(company.company_id),
        "position_id": str(position.position_id),
    }))
    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_offer(request):
    cur_user = request.user
    offer = Offer.objects.filter(offer_id=request.GET.get('offer_id')).first()
    if offer is None or offer.receiver != cur_user:
        return JsonResponse({"status": "error", "message": "Offer does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({
        'offer_id': offer.offer_id,
        'company_id': offer.company.company_id,
        'company_name': offer.company.company_name,
        'position_id': offer.position.position_id,
        'position_name': offer.position.position_name,
        'offer_at': offer.offer_at,
        'is_accepted': offer.is_accepted,
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_offer_list(request):
    cur_user = request.user
    offers = Offer.objects.filter(receiver=cur_user)
    result = []
    for offer in offers:
        result.append({
            'offer_id': offer.offer_id,
            'company': offer.company.company_name,
            'position': offer.position.position_name,
            'offer_at': offer.offer_at,
            'is_accepted': offer.is_accepted,
        })
    return JsonResponse(result, status=status.HTTP_200_OK, safe=False)

@csrf_exempt
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_offer(request):
    data = json.loads(request.body.decode('utf-8'))
    cur_user = request.user
    state = data.get('state')
    if state == 'accept':
        offer = Offer.objects.filter(offer_id=data.get('offer_id')).first()
        if offer is None or offer.receiver != cur_user:
            return JsonResponse({"status": "error", "message": "Offer does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
        offer.is_accepted = True
        Application.objects.filter(application_id=offer.application.application_id).update(result='Offer Accepted')
        offer.save()
        return JsonResponse({'status': 'success', "message": "Offer Accepted"}, status=status.HTTP_200_OK)
    else:
        offer = Offer.objects.filter(offer_id=data.get('offer_id')).first()
        if offer is None or offer.receiver != cur_user:
            return JsonResponse({"status": "error", "message": "Offer does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)
        offer.is_accepted = False
        Application.objects.filter(application_id=offer.application.application_id).update(result='Offer Rejected')
        offer.save()
        return JsonResponse({'status': 'success', "message": "Offer Rejected"}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def search_position(request):
    data = json.loads(request.body.decode('utf-8'))
    keywords = data.get('keywords', None).split()
    query = Q()
    if not keywords:
        return JsonResponse({"status": "error", "message": "keyword is required"}, status=status.HTTP_400_BAD_REQUEST)

    for keyword in keywords:
        for field in ['position_name', 'position_description']:
            query |= Q(**{f'{field}__icontains': keyword})
    positions = Position.objects.filter(query)

    data = []
    for position in positions:
        data.append({
            'position_id': position.position_id,
            'position_name': position.position_name,
            'company_name': position.company.company_name,

        })
    return JsonResponse({"status": "success", "data": PositionSerializer(results, many=True).data},
                        status=status.HTTP_200_OK)
