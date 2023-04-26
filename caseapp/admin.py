from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Case, Item, ItemForCase, OwnedCase


@admin.register(OwnedCase)
class OwnedCase(admin.ModelAdmin):
    def ung(self, obj):
        return obj.owner.usernamegame

    ung.short_description = 'Имя пользователя в игре'

    list_display = 'owner', 'ung', 'owner_id', 'case', 'item', 'date_opened'
    list_filter = 'case', 'date_opened'
    search_fields = 'owner__username', 'owner__id'
    search_help_text = 'Поиск по имени пользователя и id пользователя'
    readonly_fields = "case", "owner", "item", "date_opened", "date_owned"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = 'name', 'selling_price', 'preview', 'image'
    list_editable = 'selling_price',
    list_filter = 'image',
    readonly_fields = 'preview',
    ordering = 'selling_price',

    def preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.image}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Изображение предмета'


class ItemForCaseInline(admin.StackedInline):
    model = ItemForCase
    extra = 0


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'user_lvl_for_open', 'image')
    inlines = [ItemForCaseInline, ]
    readonly_fields = 'preview',
    ordering = ['user_lvl_for_open']

    def preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.image}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Изображение кейса'
