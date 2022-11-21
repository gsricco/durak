from django.contrib import admin

from .models import Message, UserChatRoom

class MessageInLine(admin.TabularInline):
    model = Message

@admin.register(UserChatRoom)
class UserChatRoomAdmin(admin.ModelAdmin):
    inlines = [MessageInLine]