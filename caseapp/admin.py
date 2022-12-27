from django.contrib import admin
from .models import Case, OwnedCase, Item, ItemForCase
from django.utils.safestring import mark_safe

@admin.register(OwnedCase)
class OwndedCaseAdmin(admin.ModelAdmin):
    list_display = ('case', 'owner', 'date_owned', 'date_opened','item')
    ordering = ['owner']
    search_fields = ['owner__username','owner__pk']
# admin.site.register(Item)
# admin.site.register(ItemForCase)
@admin.register(ItemForCase)
class ItemForCaseCaseAdmin(admin.ModelAdmin):
    list_display = ('case', 'item', 'chance')
    list_editable = ['chance']
    ordering = ['case']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'preview', 'selling_price', 'image')
    readonly_fields = 'preview',
    ordering = ['selling_price']
    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.image}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Изображение предмета'
class ItemForCaseInline(admin.StackedInline):
    model = ItemForCase
    extra = 0

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'user_lvl_for_open', 'image')
    inlines = [ItemForCaseInline,]
    readonly_fields = 'preview',
    ordering = ['user_lvl_for_open']
# admin.site.register(Grade)
# admin.site.register(Reward)
# admin.site.register(GivenReward)
    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.image}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Изображение кейса'