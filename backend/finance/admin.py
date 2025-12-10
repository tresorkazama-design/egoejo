from django.contrib import admin
from .models import UserWallet, WalletTransaction, EscrowContract


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'related_project', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__username', 'related_project__titre')
    readonly_fields = ('created_at',)


@admin.register(EscrowContract)
class EscrowContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'amount', 'status', 'created_at', 'released_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'project__titre')
    readonly_fields = ('created_at', 'released_at')

