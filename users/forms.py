from django.db import models
from django.db.models import fields
from django.forms import ModelForm,ValidationError
from django import forms

from .models import CsvFiles, Item, User


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name','last_name','username',
            'email','mobile','address','country',
        ]
        widgets = {
            'address' : forms.Textarea(attrs={'rows': '6' , 'cols': '10'})
        }


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = [
            'name' , 'quantity',
            'price' ,'min_quantity',
            'alerts' , 'notes'
        ]
        widgets = {
            'notes' : forms.Textarea(attrs={'rows': '3' , 'cols': '10'})
        }

    def clean_quantity(self):
        if self.cleaned_data['quantity'] <= 0:
            raise ValidationError('Quantity must be greater than 0')
        return self.cleaned_data['quantity']


class ImportForm(ModelForm):
    class Meta:
        model = CsvFiles
        fields = ['file',]