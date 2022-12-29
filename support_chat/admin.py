from django.contrib import admin

from .models import Message, UserChatRoom


@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    list_display = 'user_posted', 'chat_room',  'file_message', 'date', 'is_read', 'is_sell_item',
    readonly_fields = 'date', 'is_read', 'is_sell_item'
    fields = 'user_posted', 'chat_room', 'message', 'file_message', 'date', 'is_read', 'is_sell_item',
    list_filter = 'date', 'is_read', 'is_sell_item'#, 'file_message', 'chat_room', 'user_posted'
    search_fields = ['user_posted__username','chat_room__room_id']


@admin.register(UserChatRoom)
class UserChatRoomAdmin(admin.ModelAdmin):
    change_list_template = 'admin/admin_main_chat.html'

    def has_add_permission(self, request):
        return False  # Не отображать кнопку (+Добавить)

    def has_change_permission(self, request, obj=None):
        return False  # Не отображать кнопку (+Изменить)
