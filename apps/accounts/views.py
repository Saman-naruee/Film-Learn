from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserSerializer, PublicUserSerializer

User = get_user_model()


class IsAdminOrSelf(permissions.BasePermission):
    """
    Allow access if user is admin or it's the resource owner.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.is_staff or request.user.role == "admin":
            return True
        return obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering_fields = ["email", "date_joined", "username"]

    def get_permissions(self):
        # list and delete require admin
        if self.action in ["list", "destroy", "partial_update", "update"]:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        elif self.action in ["retrieve"]:
            permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
        elif self.action in ["create"]:
            # allow unauthenticated to register new account
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            # only return public-safe fields to non-admins
            if not (self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == "admin")):
                return PublicUserSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post"], url_path="set-password", permission_classes=[permissions.IsAuthenticated, IsAdminOrSelf])
    def set_password(self, request, pk=None):
        user = self.get_object()
        password = request.data.get("password")
        if not password:
            return Response({"detail": "password required"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({"detail": "password updated"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)
