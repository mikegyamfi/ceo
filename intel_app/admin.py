from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from import_export.admin import ExportActionMixin

from .models import OrderItem, Order


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
admin.site.register(models.Announcement)


#########################################################################
admin.site.register(models.Category)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Cart)
admin.site.register(models.Brand)
admin.site.register(models.ProductImage),
admin.site.register(models.Size)
admin.site.register(models.Color)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Number of empty forms to display in the inline


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Add the inline relationship so that OrderItem objects
    # can be managed directly on the Order admin page
    inlines = [OrderItemInline]

    # Fields to display in the Orders list
    list_display = ("tracking_number", "user", "full_name", "status", "created_at", "updated_at")

    # Enable filter sidebar
    list_filter = ("status", "region", "country", "created_at")

    # Enable search by multiple fields
    # user__username or user__email depends on which field your CustomUser uses
    search_fields = (
        "tracking_number",
        "user__username",
        "user__email",
        "full_name",
        "email",
        "phone",
        "city",
        "region",
        "payment_id",
    )

    # Some fields you may want to mark as read-only
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Fields to display in the OrderItem list
    list_display = (
        "order",
        "product",
        "price",
        "tracking_number",
        "quantity",
        "color",
        "size",
        "preorder_order_item_status",
    )

    # Enable search
    search_fields = (
        "order__tracking_number",
        "order__full_name",
        "product__name",
        "tracking_number",
    )

    # Enable filter sidebar
    list_filter = ("preorder_order_item_status", "color", "size")




