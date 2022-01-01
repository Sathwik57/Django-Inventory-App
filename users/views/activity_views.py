from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.db.models import F,Value,Count,Sum
from django.contrib import messages
from django.conf import settings  
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import csv

from users.forms import ImportForm, ItemForm
from users.utils import validate_imported_data
from ..models import DateToChar, Folder, Item, Transaction

CACHE_TTL = getattr(settings, 'CACHE_TTL')

def fetch_item(folder_slug, item_slug):
    try:
        item = Item.objects.select_related('folder').get(slug = item_slug)
        assert item.folder.slug == folder_slug
        return item
    except:
        raise Http404("No Item found" )


@cache_page(CACHE_TTL)
def home(request):
    return render(request ,'home.html')


class AddFolder(LoginRequiredMixin, CreateView):
    model = Folder
    fields = ['name','category','user']

    def form_valid(self, form):
        temp = form.save(commit = False)
        temp.user = self.request.user
        form.save()
        return super().form_valid(form)



class ListFolders(LoginRequiredMixin,ListView):
    model = Folder
    
    def get_queryset(self):
        return Folder.objects.filter(user = self.request.user).annotate(
            item_count = Count('item'),
            item_price = Sum(F('item__quantity') * F('item__price')) 
            )


class UpdateFolder(LoginRequiredMixin,UpdateView):
    model = Folder
    fields = ['name','category']

    def form_valid(self, form):
        return super().form_valid(form)


class DeleteFolder(LoginRequiredMixin,DeleteView):
    model = Folder

    def get_success_url(self):
        return reverse('activity:folders')


class AddItem(LoginRequiredMixin,CreateView):
    form_class = ItemForm
    template_name = 'users/folder_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            slug = self.kwargs.get('slug')
        except:
            raise Http404
        self.folder = get_object_or_404(Folder, slug = slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        temp = form.save(commit = False)
        temp.folder = self.folder
        form.save() 
        return HttpResponseRedirect(self.get_success_url())


class ListItem(LoginRequiredMixin,ListView):
    model = Item
    template_name= 'users/users_list.html'

    def get_queryset(self) :
        slug = self.kwargs.get('slug')
        items =  super().get_queryset().select_related('folder').filter(folder__slug = slug)
        if not items:
            raise Http404
        return items

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get('slug')
        kwargs['slug'] = slug
        kwargs['page'] = 'items'
        return super().get_context_data(**kwargs)


class ViewItem(LoginRequiredMixin,DetailView):
    model = Item
    template_name= 'users/user_detail.html'

    def get_object(self, queryset=None):     
        folder_slug = self.kwargs.get('slug') 
        item_slug = self.kwargs.get('itemslug')
        item = cache.get('item' , None)
        print(item)
        if not item:
            item =fetch_item(folder_slug, item_slug)
            cache.set('item' , item)
            print("DB Call")
        else:
            print('Cache')
        self.initial_qty = item.quantity
        return item

    def get_context_data(self, **kwargs) :
        slug = self.kwargs.get('slug')
        kwargs['slug'] = slug
        kwargs['page'] ='items'
        return super().get_context_data(**kwargs)


class UpdateItem(LoginRequiredMixin,UpdateView):
    form_class = ItemForm
    template_name= 'users/update_user.html'

    def get_object(self, queryset=None):
        folder_slug = self.kwargs.get('slug') 
        item_slug = self.kwargs.get('itemslug')
        item =fetch_item(folder_slug, item_slug)
        self.initial_qty = item.quantity
        return item

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class DeleteItem(LoginRequiredMixin,DeleteView):
    model = Item
    template_name = 'users/folder_confirm_delete.html'

    def get_object(self, queryset=None):
        folder_slug = self.kwargs.get('slug') 
        item_slug = self.kwargs.get('itemslug')
        item =fetch_item(folder_slug, item_slug)
        return item

    def get_success_url(self):
        return reverse('activity:folders')


class TransactionList(LoginRequiredMixin,ListView):
    paginate_by = 5

    def get_queryset(self):
        return  Transaction.objects.select_related('item','user','item__folder').filter(user = self.request.user)


class ExportView(LoginRequiredMixin,View):
    def get(self, request):
        response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="Inventory_summary.csv"'},
        )
        data = Item.objects.all().values_list(
            'name','quantity','price','min_quantity','notes','folder__name'
            ).annotate( 
                date_to_str1 = DateToChar(F('created'),Value('YYYY-MM-DD')),
                date_to_str2 = DateToChar(F('updated'),Value('YYYY-MM-DD'))
            )
        writer = csv.writer(response)
        writer.writerow(['name', 'quantity','price','min_quantity','notes','folder','created','updated'])
        for d in data:
            writer.writerow(d)
        return response


@login_required
def import_items(request):
    form = ImportForm()
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid:
            temp = form.save(commit= False)
            temp.user = request.user
            form.save() 
            a =validate_imported_data(temp.get_url,request)
            if a[0] == 'Success':
                messages.success(request , 'Items Imported Succesfully')
                context = {'count':len(a[1]), 'items':a[1],'page':'report'}
                return render(request,'users/import_form.html',context)
            else:
                messages.error(request , 'Import Failed')
    context ={'form': form,'page':'import'}
    return render(request,'users/import_form.html',context)


@login_required
def dashbord(request):
    low_stock= Item.get_low_stock_items().select_related('folder')
    
    items = Item.objects.select_related('folder').filter(folder__user = request.user).values_list('folder','price','quantity')
    folder_count, price ,quantity= zip(*((f, p*q, q) for f,p,q in items))
    price ,quantity ,folder_count = sum(price), sum(quantity) , len(set(folder_count))
    
    transactions = Transaction.objects.select_related('item','user').annotate(
        fold = F('item__folder__slug')).filter(user = request.user)[:5]
    
    context= {
        'low_stock': low_stock ,'item_count': items.count(),
        'folder_count': folder_count , 'price': price , 
        'transactions': transactions ,'qunatity': quantity
        
    }
    return render(request,'dashboard.html',context)