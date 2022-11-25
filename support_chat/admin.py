from django.contrib import admin

from .models import Message, UserChatRoom

# class MessageInLine(admin.TabularInline):
#     model = Message

@admin.register(UserChatRoom)
class UserChatRoomAdmin(admin.ModelAdmin):
    change_list_template = 'admin/admin_main_chat.html'
    # inlines = [MessageInLine]