from django.shortcuts import render
from django.views.generic import TemplateView
from groups.views import MyGroupListView

class HomeView(MyGroupListView):
    template_name = "home.html"
