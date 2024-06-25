from rest_framework.response import Response
from rest_framework import status
from .serializers import SubscribeCompanySerializer
from .serializers import SubscribeUserSerializer
from .models import Subscribe_user
from .models import Subscribe_company
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['POST'])
@permission_classes((AllowAny,))  # 允许任何用户访问，根据需求调整权限
def Subscribe_company(request):
    if request.method == 'POST':
        serializer = SubscribeCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes((AllowAny,))  # 允许任何用户访问，根据需求调整权限
def Subscribe_user(request):
    if request.method == 'POST':
        serializer = SubscribeUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)