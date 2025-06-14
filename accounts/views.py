# Base ViewSet with common features
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    CustomLoginSerializer,
    CustomTokenRefreshSerializer,
    CustomTokenVerifySerializer,
    UserSerializer,
)
from audits.views import AuditMixin


class AuthViewSet(viewsets.GenericViewSet, AuditMixin):
    """Handles registration, login, token refresh/verify, and logout."""

    permission_classes_by_action = {"default": [AllowAny]}

    def get_permissions(self):
        return [
            permission()
            for permission in self.permission_classes_by_action.get(
                self.action, self.permission_classes_by_action["default"]
            )
        ]

    permission_classes = [AllowAny]
    serializer_class = UserSerializer  # fallback/default

    def get_serializer_class(self):
        if self.action == "register":
            return UserSerializer
        elif self.action == "login":
            return CustomLoginSerializer
        elif self.action == "refresh":
            return CustomTokenRefreshSerializer
        elif self.action == "verify":
            return CustomTokenVerifySerializer
        return UserSerializer

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """Register a new user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self.perform_action(f"Registered new user: {user.username}", user=user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token["role"] = user.role
        access_token["email"] = user.email  # optional
        access_token["id"] = str(user.id)  # Include user ID here

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh),
                "email": user.email,
                "role": user.role,
                "id": str(user.id),  # Send user ID here
                "detail": (
                    (
                        f"{user.username}, {user.role},"
                        " you have registered successfully."
                    )
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """Obtain JWT access and refresh tokens using email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        # Add custom claims directly to the access token payload
        access_token = refresh.access_token
        access_token["role"] = user.role  # Add role here
        access_token["email"] = user.email  # Optional: add email too

        return Response(
            {
                "access": str(access_token),
                "refresh": str(refresh),
                "email": user.email,
                "role": user.role,
                "id": str(user.id),
                "detail": (
                    (
                        f"{user.username}, {user.role},"
                        " you have registered successfully."
                    )
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        """Refresh JWT access token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        """Verify JWT token validity."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "Token is valid."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        """Blacklist refresh token to logout user."""
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
