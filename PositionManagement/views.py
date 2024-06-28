import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from CompanyManagement.models import CompanyMember
from CompanyManagement.serializer import PositionSerializer
from PositionManagement.models import Position
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
    salary = data.get('salary')
    if not position_name or not position_description:
        return JsonResponse(
            {"status": "error", "message": "position_name, position_description are required"},
            status=status.HTTP_406_NOT_ACCEPTABLE)
    position = Position(company=company, position_name=position_name, position_description=position_description,
                        location=location, education_requirement=education_requirement, salary=salary)
    position.save()
    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET'])
@require_position
def get_position(request):
    position = request.position_object
    serializer = PositionSerializer(position)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


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



