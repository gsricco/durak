from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout



# def logout(request):
#     auth_logout(request)
#     return redirect('profil.html')



from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from requests import auth, request
from social_django.models import UserSocialAuth

from accaunts.models import CustomUser

# @login_required
# @auth.route('/logout')
# def profil(request):
#     logout(request)
#     try:
#         google_login = CustomUser.social_auth.get(provider='google-oauth2')
#     except UserSocialAuth.DoesNotExist:
#         google_login = None
#     context = {'google_login': google_login}
#     return render(request, 'profil.html', context)

# @auth.route('/logout')
# def profil():
#     return render(request, 'profil.html')


# from .models import CustomUser
#
#
# def logout(request):
#     context = {
#         'posts': CustomUser.objects()
#         if request.user.is_authenticated else []
#     }
#     return render(request, 'profil.html', context)



