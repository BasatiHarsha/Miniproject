from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import UserProfile

class RoleBasedAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        role = request.POST.get('role', 'student')

        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                try:
                    profile = UserProfile.objects.get(user=user)
                    if profile.role == role or (role == 'admin' and user.is_superuser):
                        return user
                except UserProfile.DoesNotExist:
                    return None
            return None
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
