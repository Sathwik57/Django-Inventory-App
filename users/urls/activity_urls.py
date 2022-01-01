from django.urls import path
from django.views.decorators.cache import cache_page

from users.views.activity_views import (
    AddFolder, AddItem, DeleteFolder, DeleteItem, ExportView,
    ListFolders, ListItem,TransactionList, UpdateFolder, UpdateItem,  
    ViewItem, dashbord, import_items,home
)

app_name = "activity"

urlpatterns = [
    path('' , home, name='home'),   
    
    path('folders/' , cache_page(60)(ListFolders.as_view()), name='folders'),
    path('folders/add/' , AddFolder.as_view(), name='add-folder'),
    path('folders/<slug>/update/' , UpdateFolder.as_view(), name='update-folder'),   
    path('folders/<slug>/delete/' , DeleteFolder.as_view(), name='delete-folder'),

    path('folders/<slug>/' , ListItem.as_view(), name='items'),
    path('folders/<slug>/add-item/' , AddItem.as_view(), name='add_item'),
    path('folders/<str:slug>/<str:itemslug>/' , ViewItem.as_view(), name='view_item'),
    path('folders/<str:slug>/<str:itemslug>/change/' , UpdateItem.as_view(), name='update_item'),
    path('folders/<str:slug>/<str:itemslug>/delete/' , DeleteItem.as_view(), name='delete_item'),
    
    path('transactions/' , TransactionList.as_view(), name='transactions'),

    path('export/' , ExportView.as_view(), name='export'),
    path('import/' , import_items, name='import'),
    path('dashboard/' , dashbord, name='dashboard'),
]