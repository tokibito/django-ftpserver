from django.contrib import admin

from .models import FTPUserGroup, FTPUserAccount


class FTPUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission')
    search_fields = ('name', 'permission')


class FTPUserAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'last_login')
    search_fields = ('user', 'group', 'last_login')

admin.site.register(FTPUserGroup, FTPUserGroupAdmin)
admin.site.register(FTPUserAccount, FTPUserAccountAdmin)
