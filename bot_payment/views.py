from django.shortcuts import render


def chat(request):
    room_name = 'go'
    context = {"room_name": room_name}
    return render(request, "bot_payment/chat.html", context)


def withdraw(request):
    room_name = 'go'
    context = {"room_name": room_name}
    return render(request, "bot_payment/chat_withdrawal.html", context)
