from django.shortcuts import render
from django.views.generic import ListView

from .models import Category


class CategoriesListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'
