from django.shortcuts import render


def chat(request):
    room_name = 'go'
    context = {"room_name": room_name}
    return render(request, "ws_chat/chat.html", context)

