from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import localtime

from . import models
from import_export.admin import ExportActionMixin

from .models import OrderItem, Order, CurrencyTransaction, CurrencyRateHistory, Currency, WalletTransaction, \
    CheckerType, ResultChecker, ResultCheckerTransaction


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
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'wallet')
        }),)


class IShareBundleTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number', 'user__username', ]


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


@admin.register(CheckerType)
class CheckerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(ResultChecker)
class ResultCheckerAdmin(admin.ModelAdmin):
    list_display = ('pin', 'serial_number', 'checker_type', 'used', 'date_added')
    list_filter = ('checker_type', 'used', 'date_added')
    search_fields = ('pin', 'serial_number')
    list_per_page = 25


@admin.register(ResultCheckerTransaction)
class ResultCheckerTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'result_checker', 'amount', 'date_bought')
    list_filter = ('user', 'date_bought')
    search_fields = ('user__username', 'result_checker__pin')
    raw_id_fields = ('user', 'result_checker')
    date_hierarchy = 'date_bought'


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


# Forex


class CurrencyRateHistoryInline(admin.TabularInline):
    model = CurrencyRateHistory
    extra = 0
    readonly_fields = ('last_update', 'last_update_rate')
    can_delete = False
    show_change_link = True


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "symbol", "rate_display", "active")
    list_filter = ("active",)
    search_fields = ("name", "short_name", "symbol")
    inlines = [CurrencyRateHistoryInline]

    def rate_display(self, obj):
        return f"P:{obj.personal_rate}-S:{obj.supplier_rate}"

    rate_display.short_description = "Current Rate"


@admin.action(description="Mark selected as Completed")
def mark_as_completed(modeladmin, request, queryset):
    updated = queryset.update(status="Completed")
    messages.success(request, f"{updated} transaction(s) marked as Completed.")


@admin.action(description="Mark selected as Refunded")
def mark_as_refunded(modeladmin, request, queryset):
    refunded_count = 0
    for tx in queryset:
        if tx.status != "Refunded":
            user = tx.user
            user.wallet += tx.amount_paid
            user.save()

            WalletTransaction.objects.create(
                user=user,
                transaction_type="Credit",
                transaction_use=f"Refund for currency transaction",
                transaction_amount=tx.amount_paid,
                new_balance=user.wallet,
            )

            tx.status = "Refunded"
            tx.save()
            refunded_count += 1
    messages.success(request, f"{refunded_count} transaction(s) successfully refunded.")


@admin.action(description="Mark selected as Pending")
def mark_as_pending(modeladmin, request, queryset):
    updated = queryset.update(status="Pending")
    messages.success(request, f"{updated} transaction(s) marked as Pending.")


@admin.action(description="Mark selected as Processing")
def mark_as_processing(modeladmin, request, queryset):
    updated = queryset.update(status="Processing")
    messages.success(request, f"{updated} transaction(s) marked as Processing.")


@admin.action(description="Mark selected as Canceled")
def mark_as_canceled(modeladmin, request, queryset):
    updated = queryset.update(status="Canceled")
    messages.success(request, f"{updated} transaction(s) marked as Canceled.")


class CurrencyTransactionForm(forms.ModelForm):
    class Meta:
        model = CurrencyTransaction
        fields = "__all__"
        widgets = {
            'status': forms.Select(choices=CurrencyTransaction._meta.get_field('status').choices)
        }


@admin.register(CurrencyTransaction)
class CurrencyTransactionAdmin(admin.ModelAdmin):
    form = CurrencyTransactionForm

    readonly_fields = ("qr_preview",)

    fields = (
        "user", "currency", "recipient_full_name", "current_currency_rate",
        "amount_paid", "amount_to_be_received", "status",
        "qr_code_for_payment", "qr_preview", "user_assigned"
    )

    list_display = (
        "user", "currency", "current_currency_rate",
        "amount_paid", "amount_to_be_received",
        "status", "transaction_date_display", "user_assigned"
    )
    list_editable = ("status",)
    list_filter = ("status", "currency", "transaction_date")
    search_fields = ("user__first_name", "user__last_name", "user__email", "currency__name")
    actions = [
        mark_as_completed,
        mark_as_refunded,
        mark_as_pending,
        mark_as_processing,
        mark_as_canceled
    ]
    autocomplete_fields = ["currency", "user", "user_assigned"]

    def transaction_date_display(self, obj):
        return localtime(obj.transaction_date).strftime('%Y-%m-%d %H:%M')

    transaction_date_display.short_description = "Transaction Date"
