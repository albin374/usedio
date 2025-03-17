from django.contrib import admin
from .models import Category, Product

# Register Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_id', 'name')  # Display these fields in the admin list view
    search_fields = ('name',)  # Enable search by category name
    ordering = ('name',)  # Allow sorting by name

# Register Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'model', 'category', 'price', 'owner', 'image')  # Display key fields
    search_fields = ('name', 'model', 'category__name')  # Enable search by product name, model, and category
    list_filter = ('category', 'owner')  # Add filter by category and owner
    ordering = ('-price',)  # Sort by price (descending)
    list_per_page = 20  # Limit the number of products displayed per page

# Register models with their respective admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
