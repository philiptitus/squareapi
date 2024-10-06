from rest_framework.permissions import BasePermission

class IsCommunityAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

    def has_object_permission(self, request, view, obj):
        return obj.community.admin == request.user
