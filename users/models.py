from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Count
from django.urls import reverse
from django.utils.text import slugify

import uuid
from django_countries.fields import CountryField

ACTIVITY = (
    ('C' , 'Create'),
    ('U' , 'Update'),
    ('M' , 'Move'),
) 

def validate_type_size(value):
    s = str(value).split('.')
    if s[-1] != 'csv':
        raise ValidationError('Only CSV Files are accepted')
    elif value.size >20_48_000:
        raise ValidationError('File size must be less than 2MB')
    return value

def validate_value(value):
    if value <0:
        raise ValidationError('Please enter value higher than 0')
    return value


class DateToChar(models.Func):
    arity = 2
    function = 'to_char'
    output_field = models.CharField() 


#Abstract class
class CommonFields(models.Model):
    '''
    This is a abstract class inherited by other models 
    '''
    name = models.CharField(max_length=100 , unique= True)
    created = models.DateField(auto_now_add= True)
    updated = models.DateTimeField(auto_now_add= True)

    class Meta:
        abstract = True

class User(AbstractUser):
    '''
    Custom User class
    '''
    mobile = models.BigIntegerField(null=True , blank = True,  unique= True)
    address = models.TextField(null=True , blank = True)
    country = CountryField(null= True, blank = True)
    created = models.DateTimeField(auto_now_add= True)
    id = models.UUIDField(default = uuid.uuid4, primary_key= True, editable= False, unique= True)

    def __str__(self) -> str:
        return self.username.title()

    def get_absolute_url(self):
        return reverse("users:detail",kwargs={'username': self.username})


class Category(models.Model):
    '''
    Folder categories
    '''
    name = models.CharField(max_length=100 , unique= True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name',]
    
    def __str__(self) -> str:
        return self.name.title()
    

class Folder(CommonFields):
    '''
    Folder model to store Items
    '''
    user = models.ForeignKey(User , related_name = 'user' ,on_delete= models.CASCADE)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL , null= True)
    id = models.BigAutoField(primary_key=True,editable=False,unique=True)

    class Meta(CommonFields.Meta):
        ordering = ['created','name']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Folder ,self).save(*args , **kwargs)

    def __str__(self) -> str:
        return self.name.title()

    def get_absolute_url(self):
        return reverse('activity:view-folder', kwargs={'slug':self.slug})

    def get_item_count(self):
        return self.item_set.values('name').count()

    def get_item_price(self):
        return sum((item[0]*item[1] for item in self.item_set.values_list('price','quantity'))) 


class Item(CommonFields):
    # TODO: Add tags to filter items by Tags  
    
    id = models.BigAutoField(primary_key=True,editable=False,unique=True)
    folder = models.ForeignKey(Folder,on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    quantity = models.IntegerField(default=1, validators=[validate_value])
    price = models.FloatField(default=0,blank=True,validators=[validate_value])
    min_quantity = models.IntegerField(null=True,blank=True)
    alerts = models.BooleanField(default=False,blank=True)
    notes = models.TextField(null= True, blank= True)
    prev_quantity = models.IntegerField(null=True, blank= True,default=0)
 
    class Meta(CommonFields.Meta):
        ordering =['-created',]

    def __init__(self , *args, **kwargs):  
        super(Item,self).__init__(*args, **kwargs)  

    def __str__(self) -> str:
        return self.name.title() + '-' + str(self.id)

    def clean(self):
        if self.alerts and not self.min_quantity:
            raise ValidationError('Please specify low stock quantity(min quantity) to enable alerts')
        return super().clean()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.pk:
            self.prev_quantity = Item.objects.values('quantity').get(id = self.pk)['quantity']
        super(Item ,self).save(*args , **kwargs)    
        
    def get_absolute_url(self):
        return reverse('activity:view_item', kwargs={'slug':self.folder.slug ,'itemslug':self.slug})

    @property
    def get_price(self):
        return self.price * self.quantity


    @classmethod
    def get_low_stock_items(cls):
        return cls.objects.filter(min_quantity__gte = F('quantity'))

    @property
    def is_low(self):
        return self.min_quantity >= self.quantity if self.min_quantity else False


class Transaction(models.Model):
    id = models.UUIDField(default = uuid.uuid4, primary_key= True, editable= False, unique= True)
    date = models.DateField(auto_now_add= True, editable=False)
    user = models.ForeignKey(User,on_delete= models.CASCADE )
    item = models.ForeignKey(Item , on_delete=models.CASCADE,related_name= 'item')
    qty_change = models.IntegerField()
    activity = models.CharField(choices= ACTIVITY , max_length=1)
    notes = models.CharField(max_length=150 , null=True ,blank=True)     

    class Meta:
        ordering = ['-date']

    def __str__(self) -> str:
        return f'{self.item.name} - {self.activity} , {self.date}'


class CsvFiles(models.Model):
    user = models.ForeignKey(User,on_delete= models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='files', validators= [validate_type_size,])

    class Meta:
        ordering = ['date']

    @property
    def get_url(self):
        return self.file.url


class Stat(models.Model):
    win = models.IntegerField()
    mac = models.IntegerField()
    android = models.IntegerField()
    ios = models.IntegerField()
    others = models.IntegerField() 