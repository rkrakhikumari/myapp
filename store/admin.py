from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Color)  # Register ProductColor for admin management
admin.site.register(ProductSize)
admin.site.register(Cart)
admin.site.register(CartHistory)


admin.site.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     pass
    # list_display = ('id', 'user', 'created_at', 'total_price', 'address', 'phone_number', 'email')
    # search_fields = ('user__username', 'id', 'phone_number', 'email')
    # readonly_fields = ('cart_details', 'id', 'user', 'total_price', 'address', 'phone_number', 'email', 'created_at')
    
    # fields = (
    #     'id',
    #     'user',
    #     'phone_number',
    #     'email',
    #     'address',
    #     'total_price',
    #     'cart_details',
    #     'created_at',
    #     'items',  # if you want to see related cart items
    # )
