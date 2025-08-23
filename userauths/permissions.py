from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    """
    يسمح فقط للـ users اللي هو vendor
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and hasattr(user, "vendor")  
            and user.vendor is not None   
        )
