from django.urls import path

from ..views.user_views import Profile, UpdateProfile, UserList, home

app_name = "users"
urlpatterns = [
    path('' , UserList.as_view(), name='users_list'),
    path('<str:username>/change' , UpdateProfile.as_view(), name='update'),
    path('<str:username>/' , Profile.as_view(), name='detail'),

]