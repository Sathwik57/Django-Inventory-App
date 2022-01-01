from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic import UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from ..forms import ProfileForm
from ..models import  User

class UserList(LoginRequiredMixin, ListView):
    template_name = 'users/users_list.html'
    queryset = User.objects.all()

    def get_context_data(self, **kwargs) :
        kwargs['page'] ='users'
        return super().get_context_data(**kwargs)


class UpdateProfile(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'users/update_user.html'
    queryset = User.objects.all()
    slug_field = "username"
    slug_url_kwarg = "username"

    def test_func(self):
        return self.request.user.username == self.kwargs.get('username',None)


class Profile(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def test_func(self):
        return self.request.user.username == self.kwargs.get('username',None)

    def get_context_data(self, **kwargs) :
        kwargs['page'] ='users'
        return super().get_context_data(**kwargs)


class DeleteProfile(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    
    def test_func(self):
        return self.request.user.username == self.kwargs.get('username',None)

    def get_success_url(self):
        return reverse('activity:')