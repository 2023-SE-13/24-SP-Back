import json

from django.core.files import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view

from CompanyManagement.models import Company, CompanyMember


# Create your views here.
@api_view(['PUT'])
def create_company(request):
    data = json.loads(request.body.decode('utf-8'))
    company_name = data.get('company_name')
    company_description = data.get('company_description')
    if not company_name or not company_description:
        return JsonResponse(
            {"status": "error", "message": "company_name, company_description are required"},
            status=status.HTTP_400_BAD_REQUEST)

    company = Company.objects.filter(company_name=company_name)
    if company.exists():
        return JsonResponse({"status": "error", "message": "Company name already exists"}, status=status.HTTP_409_CONFLICT)

    company = Company(company_name=company_name, company_description=company_description)
    company.save()
    company_id = company.id
    # 设置默认image
    default_image_path = 'resources/company_images/default_image.png'
    with open(default_image_path, 'rb') as f:
        image_content = f.read()
    new_filename = f"{company_id}_image.png"
    new_file = ContentFile(image_content)
    new_file.name = new_filename
    company.company_image.save(new_filename, new_file, save=True)

    # 将创建者加入Company
    user = request.user
    company_member = CompanyMember(company=company, user=user, role='Creator')
    company_member.save()

    return JsonResponse({'status': 'success'}, status=status.HTTP_201_CREATED)
