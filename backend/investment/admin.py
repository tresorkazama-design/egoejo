from django.contrib import admin
from .models import ShareholderRegister


@admin.register(ShareholderRegister)
class ShareholderRegisterAdmin(admin.ModelAdmin):
    list_display = ('investor', 'project', 'number_of_shares', 'amount_invested', 'is_signed', 'created_at')
    list_filter = ('is_signed', 'created_at')
    search_fields = ('investor__username', 'project__titre')
    readonly_fields = ('created_at', 'updated_at')
