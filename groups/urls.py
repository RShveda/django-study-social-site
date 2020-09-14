"""django_social_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from .views import (GroupCreateView, GroupDetailView, GroupDeleteView,
                        GroupUpdateView, GroupListView, MyGroupListView,
                        GroupJoinView, GroupLeaveView)

app_name = "groups"

urlpatterns = [
    path('', GroupListView.as_view(), name='group_list'),
    path('mygroups/', MyGroupListView.as_view(), name='my_group_list'), #not used
    path('<slug:slug>/detail/', GroupDetailView.as_view(), name='group_detail'),
    path('<slug:slug>/delete/', GroupDeleteView.as_view(), name='group_delete'),
    path('new/', GroupCreateView.as_view(), name='group_create'),
    path('<slug:slug>/edit/', GroupUpdateView.as_view(), name='group_edit'),
    path('<slug:slug>/join/', GroupJoinView.as_view(), name='group_join'),
    path('<slug:slug>/leave/', GroupLeaveView.as_view(), name='group_leave'),
]
