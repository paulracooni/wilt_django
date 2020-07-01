from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsAuthorOrReadonly(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has object_permission(slef, request. views, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.author == request.user

class IsAuthorUpdateOrReadOnly(BasePermission):

    def has_permission(slef, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if (request.method == 'DELETE'):
            return request.user.is_superuser
        
        return obj.author == request.user