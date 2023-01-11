from django.core.exceptions import PermissionDenied
from accaunts.models import Ban, UserIP, UserAgent, CustomUser


class BanIPandAgentMiddleware:
    """Проводим проверку входящего запроса по IP и UserAgent на бан по ban_ip"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agent = (request.META['HTTP_USER_AGENT'])
        ip = request.META.get("HTTP_X_REAL_IP")
        # ip = (request.META['REMOTE_ADDR'])
        # all_ban_ip = Ban.objects.filter(ban_ip=True)
        # list_ban_ip_agent = []
        # for ban in all_ban_ip:
        #     list_ban_ip_agent.extend([i.userip for i in UserIP.objects.filter(user_id=ban.user_id)])
        #     list_ban_ip_agent.extend([a.useragent for a in UserAgent.objects.filter(user_id=ban.user_id)])
        #     if ip in list_ban_ip_agent and agent in list_ban_ip_agent:
        #         raise PermissionDenied
        #     list_ban_ip_agent = []
        if CustomUser.objects.filter(userip__userip=ip, useragent__useragent=agent, ban__ban_ip=True).exists():
            print(CustomUser.objects.filter(userip__userip=ip, useragent__useragent=agent, ban__ban_ip=True))
            raise PermissionDenied
        if request.user.is_authenticated:
            if not request.user.userip_set.filter(userip=ip).exists():
                UserIP.objects.create(userip=ip, user=request.user)
            if not request.user.useragent_set.filter(useragent=agent).exists():
                UserAgent.objects.create(useragent=agent, user=request.user)
        response = self.get_response(request)
        return response



