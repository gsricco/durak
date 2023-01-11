from django.core.exceptions import PermissionDenied
from accaunts.models import Ban, UserIP, UserAgent


class BanIPandAgentMiddleware:
    """Проводим проверку входящего запроса по IP и UserAgent на бан по ban_ip"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agent = (request.META['HTTP_USER_AGENT'])
        ip = (request.META['REMOTE_ADDR'])
        all_ban_ip = Ban.objects.filter(ban_ip=True)
        list_ban_ip_agent = []
        for ban in all_ban_ip:
            list_ban_ip_agent.extend([i.userip for i in UserIP.objects.filter(user_id=ban.user_id)])
            list_ban_ip_agent.extend([a.useragent for a in UserAgent.objects.filter(user_id=ban.user_id)])
            # print(list_ban_ip_agent)
            if ip in list_ban_ip_agent and agent in list_ban_ip_agent:
                print(ban.user)
                raise PermissionDenied
            list_ban_ip_agent = []
        response = self.get_response(request)
        return response


def add_new_ip(get_response):

    def mw(request):
        if request.user.is_authenticated:
            ip1 = (request.META['REMOTE_ADDR'])
            ip = request.META.get("HTTP_X_REAL_IP")
            print(ip, 'ETO IP FROM HTTP_X_REAL_IP')
            print(ip1, "ETO IP FROM REMOTE ADDR")
            if not request.user.userip_set.filter(userip=ip).exists():
                # print(request.user.userip_set.filter(userip=ip1).exists())
                UserIP.objects.create(userip=ip, user=request.user)
                # UserIP.objects.create(userip=ip2, user=request.user)
            response = get_response(request)
            return response
    return mw