from django.contrib import admin

from . import models


class FTPUserGroupAdmin(admin.ModelAdmin):
    """Admin class for FTPUserGroup"""

    list_display = ("name", "permission")
    search_fields = ("name", "permission")


class FTPUserAccountAdmin(admin.ModelAdmin):
    """Admin class for FTPUserAccountAdmin"""

    list_display = ("user", "group", "last_login")
    search_fields = ("user", "group", "last_login")
    raw_id_fields = ("user",)


admin.site.register(models.FTPUserGroup, FTPUserGroupAdmin)
admin.site.register(models.FTPUserAccount, FTPUserAccountAdmin)
