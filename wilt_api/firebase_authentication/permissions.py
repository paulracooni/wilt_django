from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAuthenticatedOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(slef, request, views, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsMyself(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(slef, request, views, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id


class IsAuthor(permissions.BasePermission):
    def has_permission(slef, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user.id == request.user.id


class IsAuthorOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(slef, request, views, obj):

        if request.method in permissions.SAFE_METHODS:
            return True
        print(obj.user == request.user)
        return obj.user == request.user


class IsAuthorUpdateOrReadOnly(permissions.BasePermission):
    def has_permission(slef, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return request.user.is_superuser

        return obj.user == request.user
