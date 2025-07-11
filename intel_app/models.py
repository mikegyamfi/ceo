import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import format_html

from intel_app.custom_storages import MediaStorage


# from intel_app.custom_storages import MediaStorage


# Create your models here.


# Create your models here.
class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=250, null=False, blank=False)
    phone = models.PositiveIntegerField(null=True, blank=True)
    wallet = models.FloatField(null=True, blank=True, default=0.0)
    choices = (
        ("User", "User"),
        ("Agent", "Agent"),
        ("Super Agent", "Super Agent")
    )
    status = models.CharField(max_length=250, null=False, blank=False, choices=choices)
    password1 = models.CharField(max_length=100, null=False, blank=False)
    password2 = models.CharField(max_length=100, null=False, blank=False)
    forex_status_choices = (
    ("Personal", "Personal"),
    ("Supplier", "Supplier")
    )
    forex_status = models.CharField(max_length=250, null=True, blank=True, choices=forex_status_choices, default="Personal")

    def __str__(self):
        return self.username


class AdminInfo(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.BigIntegerField(null=True, blank=True)
    momo_number = models.PositiveBigIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    forex_minimum_amount = models.FloatField(null=False, blank=False, default=200)
    choices = (
        ("MTN Mobile Money", "MTN Mobile Money"),
        ("Vodafone Cash", "Vodafone Cash"),
        ("AT Money", "AT Money")
    )
    payment_channel = models.CharField(max_length=250, choices=choices)
    afa_price = models.FloatField(null=True, blank=True)
    paystack_active = models.BooleanField(default=False)
    paystack_active_commerce = models.BooleanField(default=False)
    ishare_choices = (
        ("Geosams", "Geosams"),
        ("Noble", "Noble")
    )
    ishare_source = models.CharField(max_length=300, default="Geosams", choices=ishare_choices)
    send_sms_for_forex = models.BooleanField(default=False)


class IShareBundleTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bundle_number = models.BigIntegerField(null=False, blank=False)
    offer = models.CharField(max_length=250, null=False, blank=False)
    reference = models.CharField(max_length=250, null=False, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.bundle_number} - {self.reference}"


class AgentIshareBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class SuperAgentIshareBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class IshareBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class AgentBigTimeBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class SuperAgentBigTimeBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class BigTimeBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class AgentTelecelBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class SuperAgentTelecelBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class TelecelBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class BigTimeTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bundle_number = models.BigIntegerField(null=False, blank=False)
    amount = models.FloatField(null=True, blank=True)
    offer = models.CharField(max_length=250, null=False, blank=False)
    reference = models.CharField(max_length=250, null=False, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    choices = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    )
    transaction_status = models.CharField(max_length=100, choices=choices, default="Pending")
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.bundle_number} - {self.reference}"


class AFARegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_number = models.BigIntegerField(null=False, blank=False)
    gh_card_number = models.CharField(null=False, blank=False, max_length=256)
    name = models.CharField(max_length=250, null=False, blank=False)
    occupation = models.CharField(max_length=250, null=False, blank=True)
    reference = models.CharField(max_length=250, null=False, blank=True)
    date_of_birth = models.DateField(null=False, blank=False)
    choices = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    )
    transaction_status = models.CharField(max_length=100, choices=choices, default="Pending")
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number} - {self.gh_card_number}"


class MTNTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bundle_number = models.BigIntegerField(null=False, blank=False)
    offer = models.CharField(max_length=250, null=False, blank=False)
    amount = models.FloatField(null=True, blank=True)
    reference = models.CharField(max_length=250, null=False, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    choices = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    )
    transaction_status = models.CharField(max_length=100, choices=choices, default="Pending")
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.bundle_number} - {self.reference}"


class TelecelTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bundle_number = models.BigIntegerField(null=False, blank=False)
    offer = models.CharField(max_length=250, null=False, blank=False)
    amount = models.FloatField(null=True, blank=True)
    reference = models.CharField(max_length=250, null=False, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    choices = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed")
    )
    transaction_status = models.CharField(max_length=100, choices=choices, default="Pending")
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.bundle_number} - {self.reference}"


class MTNBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class AgentMTNBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class SuperAgentMTNBundlePrice(models.Model):
    price = models.FloatField(null=False, blank=False)
    bundle_volume = models.FloatField(null=False, blank=False)

    def __str__(self):
        if self.bundle_volume >= 1000:
            return f"GHS{self.price} - {self.bundle_volume / 1000}GB"
        return f"GHS{self.price} - {self.bundle_volume}MB"


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reference = models.CharField(max_length=256, null=False, blank=False)
    amount = models.FloatField(null=True, blank=True)
    payment_description = models.CharField(max_length=500, null=True, blank=True)
    transaction_status = models.CharField(max_length=256, null=True, blank=True, default="Unfinished")
    transaction_date = models.CharField(max_length=250, null=True, blank=True)
    message = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.reference}"


class TopUpRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reference = models.CharField(max_length=250, null=False, blank=False)
    amount = models.FloatField(blank=False, null=False)
    status = models.BooleanField(default=False, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    credited_at = models.DateTimeField(auto_now_add=True)


####################################################################################

def get_file_path(filename):
    original_filename = filename
    nowTime = datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (nowTime, original_filename)
    return os.path.join('uploads/', filename)


class Brand(models.Model):
    name = models.CharField(max_length=250, null=False, blank=False, default="Generic")
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    slug = models.CharField(max_length=250, null=False, blank=False)
    name = models.CharField(max_length=250, null=False, blank=True)
    image = models.ImageField(upload_to='category/', null=True, blank=True, storage=MediaStorage())
    # image = models.ImageField(upload_to='category/', null=True, blank=True)
    description = models.TextField(max_length=600, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="0=default, 1=Hidden")
    trending = models.BooleanField(default=False, help_text="0=default, 1=Trending")
    meta_title = models.CharField(max_length=150, null=True, blank=True)
    meta_keywords = models.CharField(max_length=150, null=True, blank=True)
    meta_description = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    size = models.CharField(null=False, blank=False, max_length=250)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.size


class Color(models.Model):
    choices = (
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
        ('pink', 'Pink'),
        ('brown', 'Brown'),
        ('black', 'Black'),
        ('white', 'White'),
        ('gray', 'Gray'),
        ('cyan', 'Cyan'),
        ('magenta', 'Magenta'),
        ('lime', 'Lime'),
        ('indigo', 'Indigo'),
        ('violet', 'Violet'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('maroon', 'Maroon'),
        ('olive', 'Olive'),
        ('teal', 'Teal'),
        ('navy', 'Navy'),
        ('beige', 'Beige'),
        ('coral', 'Coral'),
        ('salmon', 'Salmon'),
        ('khaki', 'Khaki'),
        ('plum', 'Plum'),
        ('orchid', 'Orchid'),
        ('turquoise', 'Turquoise'),
        ('lavender', 'Lavender'),
        ('Bronze', 'Bronze'),
        ('Blue-Black', 'Blue-Black'),
        ('Rose', 'Rose')
    )
    color = models.CharField(null=False, blank=False, max_length=250, choices=choices)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.color


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=250, blank=True)
    description = models.TextField(max_length=600, blank=False)
    quantity = models.PositiveIntegerField(blank=False)
    original_price = models.FloatField(blank=False)
    selling_price = models.FloatField(blank=False)
    status = models.BooleanField(default=False, help_text="0=default, 1=Hidden")
    trending = models.BooleanField(default=False, help_text="0=default, 1=Trending")
    sizes = models.ManyToManyField(Size, blank=True)
    colors = models.ManyToManyField(Color, blank=True)
    tag = models.CharField(max_length=150, blank=False)
    meta_title = models.CharField(max_length=150, blank=True)
    meta_keywords = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    preorder_item = models.BooleanField(default=False)
    preorder_end_date = models.DateField(null=True, blank=True)
    preorder_arrival_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, storage=MediaStorage())
    # image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_qty = models.PositiveIntegerField(null=False, blank=False)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(max_length=150, null=False)
    phone = models.PositiveIntegerField(null=False)
    address = models.TextField(null=False)
    city = models.CharField(max_length=150, null=False)
    REGIONS_CHOICES = (
        ('Ashanti Region', 'Ashanti Region'),
        ('Brong-Ahafo Region', 'Brong-Ahafo Region'),
        ('Central Region', 'Central Region'),
        ('Eastern Region', 'Eastern Region'),
        ('Greater Accra Region', 'Greater Accra Region'),
        ('Northern Region', 'Northern Region'),
        ('Oti Region', 'Oti Region'),
        ('Upper East Region', 'Upper East Region'),
        ('Upper West Region', 'Upper West Region'),
        ('Volta Region', 'Volta Region'),
        ('Western Region', 'Western Region'),
        ('Western North Region', 'Western North Region'),
    )
    region = models.CharField(max_length=150, null=False, blank=False, choices=REGIONS_CHOICES)
    country = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=150, null=True, blank=True)
    total_price = models.FloatField(null=False)
    payment_mode = models.CharField(max_length=150, null=True)
    payment_id = models.CharField(max_length=250, null=True, blank=True)
    order_statuses = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled')
    )
    status = models.CharField(max_length=50, choices=order_statuses, default="Pending")
    customer_mark_as_received = models.BooleanField(default=False)
    message = models.TextField(null=True)
    tracking_number = models.CharField(max_length=150, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tracking_number} - {self.user} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    tracking_number = models.CharField(max_length=150, null=True)
    quantity = models.PositiveIntegerField(null=False)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)
    choices = (
        ('Delivered', 'Delivered'),
        ('Arrived', 'Arrived')
    )
    preorder_order_item_status = models.CharField(max_length=250, null=True, choices=choices)

    def __str__(self):
        return f"{self.order.tracking_number} - {self.order.user} - {self.order.full_name}"


class WalletTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    choices = (
        ("Debit", "Debit"),
        ("Credit", "Credit"),
    )
    transaction_type = models.CharField(max_length=250, null=True, blank=True, choices=choices)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_use = models.CharField(max_length=250, null=True, blank=True)
    transaction_amount = models.FloatField(null=False)
    new_balance = models.FloatField(null=True)


class CheckerType(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=250, null=True, blank=True)
    price = models.FloatField(null=False)

    def __str__(self):
        return self.name


class ResultChecker(models.Model):
    checker_type = models.ForeignKey(CheckerType, on_delete=models.CASCADE)
    pin = models.CharField(max_length=150, null=False, blank=False)
    serial_number = models.CharField(max_length=150, null=False, blank=False)
    used = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.checker_type.name} — {self.pin} / {self.serial_number}"


class ResultCheckerTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    result_checker = models.ForeignKey(ResultChecker, on_delete=models.CASCADE)
    date_bought = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(null=False)

    def __str__(self):
        return f"{self.user.username} bought {self.result_checker.pin} on {self.date_bought.date()}"


class Announcement(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.CharField(max_length=500, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.message


class Currency(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)
    short_name = models.CharField(max_length=250, null=True, blank=True)
    symbol = models.CharField(max_length=300, null=True, blank=True)
    personal_rate = models.FloatField()
    supplier_rate = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}({self.symbol})"


class CurrencyRateHistory(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now_add=True)
    last_update_rate = models.FloatField(null=False)


class CurrencyTransaction(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipient_full_name = models.CharField(max_length=250, null=True, blank=True)
    current_currency_rate = models.FloatField(null=False)
    amount_paid = models.FloatField(null=False)
    qr_code_for_payment = models.ImageField(upload_to='payment_qr_codes/', blank=True, null=True, storage=MediaStorage())
    status_choices = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
        ("Refunded", "Refunded"),
    )
    status = models.CharField(max_length=250, null=True, blank=True, choices=status_choices, default="Pending")
    transaction_date = models.DateTimeField(auto_now_add=True)
    user_assigned = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='provider')
    amount_to_be_received = models.FloatField(null=False)

    def qr_preview(self):
        if self.qr_code_for_payment:
            return format_html('<img src="{}" style="max-height: 150px;" />', self.qr_code_for_payment.url)
        return "(No image)"

    qr_preview.short_description = "QR Code Preview"

    def __str__(self):
        return f"{self.user.first_name}-{self.currency}"
