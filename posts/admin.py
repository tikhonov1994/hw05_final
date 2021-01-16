from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('title', 'slug', 'description')


admin.site.register(Group, GroupAdmin)
