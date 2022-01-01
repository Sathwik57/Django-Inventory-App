from django.db import transaction
from django.templatetags.static import static
from django.utils.text import slugify

from numpy import nan
import pandas as pd

from users.models import Folder, Item, Transaction

def func(value):
    try:
        if value == nan:
            return nan
        else:
            a = int(value)
            return a if a> 0  else nan
    except ValueError:
        return nan

def validate_imported_data(file_url,request):
    #Read CSV data
    file_url = 'C:/Projects_Python/sortly/' +static(file_url)
    df = pd.read_csv(file_url)
    
    #Drop rows with no name
    df.dropna(subset=['name'], inplace= True) 
    
    #Check for invalid entries and set alerts false if min_quantity is not present 
    df['min_quantity'] = df['min_quantity'].apply(func)
    filt2 = df['min_quantity'].isna()
    df.loc[filt2,'alerts'] = False

    #check for invalid entries
    df['price']=  df['price'].apply(func)

    #Check for invalid entries and remove including null fields
    df['quantity'] = df['quantity'].apply(func)
    df.dropna(subset=['quantity',], inplace =True)
    
    df['price'] = df['price'].replace({nan: None})
    df['min_quantity'] = df['min_quantity'].replace({nan: None})

    c =Folder.objects.select_related('user').filter(name__contains= 'Bulk_import').count() + 1

    with transaction.atomic():
        fold = Folder.objects.create(
            user =request.user,
            name = f'Bulk_import_{c}',
            )

        try:
            bulk_append = [
                Item(
                    name = df.loc[x]['name'],
                    folder = fold,
                    slug = slugify(df.loc[x]['name']),
                    quantity = df.loc[x]['quantity'],
                    price = df.loc[x]['price'] if  df.loc[x]['price']!= nan else None,
                    alerts = df.loc[x]['alerts'],
                    min_quantity = df.loc[x]['min_quantity'] if  df.loc[x]['min_quantity']!= nan else None,
                    notes = df.loc[x]['notes']
                )
                for x in df.index
            ]
            item_list = Item.objects.bulk_create(bulk_append)
            transact_list = [
                Transaction(
                user = request.user,
                item= item,
                qty_change = item.quantity,
                activity = 'C',
                notes = 'Bulk Import'
                )
                for item in item_list
            ]
            Transaction.objects.bulk_create(transact_list)
            return ('Success',[df.loc[x]['name'] for x in df.index])

        except Exception as e:
            return ('Error',e)