from django.core.exceptions import PermissionDenied

from accaunts.models import Ban, CustomUser, UserAgent, UserIP


class BanIPandAgentMiddleware:
    """Проводим проверку входящего запроса по IP и UserAgent на бан по ban_ip"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agent = request.META.get('HTTP_USER_AGENT')
        ip = request.META.get("HTTP_X_REAL_IP")
        print(ip)
        if CustomUser.objects.filter(userip__userip=ip, useragent__useragent=agent, ban__ban_ip=True).exists():
            raise PermissionDenied
        if request.user.is_authenticated:
            if not request.user.userip_set.filter(userip=ip).exists():
                UserIP.objects.create(userip=ip, user=request.user)
            if not request.user.useragent_set.filter(useragent=agent).exists():
                UserAgent.objects.create(useragent=agent, user=request.user)
        response = self.get_response(request)
        return response
