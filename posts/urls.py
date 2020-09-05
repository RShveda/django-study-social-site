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
from .views import (PostCreateView, PostDeleteView, PostUpdateView, PostVoteView,
                    PostRemoveVoteView)

app_name = "posts"

urlpatterns = [
    path('<slug:group>/new/', PostCreateView.as_view(), name='post_create'),
    path('<pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('<pk>/vote/', PostVoteView.as_view(), name='post_vote'),
    path('<pk>/remove_vote/', PostRemoveVoteView.as_view(), name='post_remove_vote'),
]
