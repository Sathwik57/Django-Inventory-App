from django.contrib import admin

from .models import Category, CsvFiles, Folder, Item, Stat, Transaction, User

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(CsvFiles)


class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'user', 'category']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['name','folder','price','quantity',]
    list_editable = ['price','quantity',]


class StatAdmin(admin.ModelAdmin):
    list_display = ['win','mac','android','ios','others']


admin.site.register(Item, ItemAdmin)
admin.site.register(Folder,FolderAdmin)
admin.site.register(Stat, StatAdmin)