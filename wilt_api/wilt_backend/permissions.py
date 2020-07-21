from wilt_api.settings import DEBUG
from rest_framework import permissions

is_deveolper = lambda request: getattr(request.user, "is_superuser", False) and DEBUG


class AllowAny(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(slef, request, views, obj):
        return True


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_deveolper(request):
            return True
        return bool(request.user and request.user.is_authenticated)


class IsAuthenticatedOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(slef, request, views, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsMyself(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_deveolper(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(slef, request, views, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id


class IsAuthor(permissions.BasePermission):
    def has_permission(slef, request, view):
        if is_deveolper(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user.id == request.user.id


class IsAuthorOrAllowAnonymousGet(permissions.BasePermission):
    def has_permission(slef, request, view):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user.id == request.user.id


class IsAuthorOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        if is_deveolper(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(slef, request, views, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        print(obj.user == request.user)
        return obj.user == request.user


class IsAuthorUpdateOrReadOnly(permissions.BasePermission):
    def has_permission(slef, request, view):
        if is_deveolper(request):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if is_deveolper(request):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return request.user.is_superuser

        return obj.user == request.user
