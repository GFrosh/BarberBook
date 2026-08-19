from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, tokens_for_user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    s = RegisterSerializer(data=request.data); s.is_valid(raise_exception=True)
    user = s.save()
    return Response({'user': UserSerializer(user).data, 'tokens': tokens_for_user(user)},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    s = LoginSerializer(data=request.data); s.is_valid(raise_exception=True)
    user = s.validated_data['user']
    return Response({'user': UserSerializer(user).data, 'tokens': tokens_for_user(user)})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        refresh = request.data.get('refresh')
        if refresh:
            RefreshToken(refresh).blacklist()
    except Exception:
        pass
    return Response({'detail': 'Logged out.'})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)
    s = UserSerializer(request.user, data=request.data, partial=True); s.is_valid(raise_exception=True)
    s.save()
    return Response(s.data)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAdminUser]
