from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from import_export.admin import ExportActionMixin


# Register your models here.
class CustomUserAdmin(ExportActionMixin, UserAdmin):
    list_display = ['first_name', 'last_name', 'username', 'email', 'wallet', 'phone', 'status']

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Other Personal info',
            {
                'fields': (
                    'phone', 'wallet', 'status'
                )
            }
        )
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2', 'wallet')
        }),)
    

class IShareBundleTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number', 'user__username',]


class MTNTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number', 'user__username']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'reference', 'transaction_date', 'amount']


class TopUpRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'reference', 'amount', 'date', 'status']


class ProductImageInline(admin.TabularInline):  # or admin.StackedInline
    model = models.ProductImage
    extra = 4  # Set the number of empty forms to display


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    search_fields = ['name']


class VodafoneTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number']


class BigTimeTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number']


class AFATransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'gh_card_number', 'name', 'reference', 'date_of_birth', 'transaction_date']
    search_fields = ['reference', 'gh_card_number', 'user__username']


class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'transaction_amount', 'transaction_use', 'new_balance',
                    'transaction_date']
    search_fields = ['transaction_type', 'user__username', 'transaction_amount', 'transaction_use']


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.IShareBundleTransaction, IShareBundleTransactionAdmin)
admin.site.register(models.MTNTransaction, MTNTransactionAdmin)
admin.site.register(models.IshareBundlePrice)
admin.site.register(models.MTNBundlePrice)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.AdminInfo)
admin.site.register(models.TopUpRequest, TopUpRequestAdmin)
admin.site.register(models.AgentIshareBundlePrice)
admin.site.register(models.AgentMTNBundlePrice)
admin.site.register(models.SuperAgentIshareBundlePrice)
admin.site.register(models.AFARegistration, AFATransactionAdmin)
admin.site.register(models.BigTimeTransaction, BigTimeTransactionAdmin)
admin.site.register(models.SuperAgentMTNBundlePrice)
admin.site.register(models.BigTimeBundlePrice)
admin.site.register(models.AgentBigTimeBundlePrice)
admin.site.register(models.SuperAgentBigTimeBundlePrice)
admin.site.register(models.TelecelBundlePrice)
admin.site.register(models.AgentTelecelBundlePrice)
admin.site.register(models.SuperAgentTelecelBundlePrice)
admin.site.register(models.TelecelTransaction, VodafoneTransactionAdmin)
admin.site.register(models.WalletTransaction, WalletTransactionAdmin)
admin.site.register(models.CheckerType)
admin.site.register(models.ResultChecker)
admin.site.register(models.ResultCheckerTransaction)


#########################################################################
admin.site.register(models.Category)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Cart)
admin.site.register(models.OrderItem)
admin.site.register(models.Order)
admin.site.register(models.Brand)
admin.site.register(models.ProductImage),
admin.site.register(models.Size)
admin.site.register(models.Color)
