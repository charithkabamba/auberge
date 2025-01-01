from django.urls import path

from . import views

app_name = 'categories'

urlpatterns = [
    path('all-categories', views.CategoriesListView.as_view(), name='all_categories'),
]
