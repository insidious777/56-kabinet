from django.contrib import admin
from django.utils.decorators import method_decorator

from common.decorators import preserve_help_text
from menu.models import MenuItem, MenuCategory, Action, Addition


@admin.register(MenuCategory)
class MenuCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index', 'can_order', 'show')
    search_fields = ('name', 'title')
    ordering = ('order_index',)
    list_filter = ('show',)


@admin.register(MenuItem)
@method_decorator(preserve_help_text, name='formfield_for_manytomany')
class MenuItemModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'volume', 'show')
    search_fields = ('title', 'description', 'price')
    list_filter = ('show', 'category')


@admin.register(Action)
class ActionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index', 'show')
    search_fields = ('name',)
    list_filter = ('show',)
    ordering = ('order_index',)


@admin.register(Addition)
class AdditionModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'show')
    search_fields = ('title', 'price')
    list_filter = ('show',)
