from django.shortcuts import render
from django.views.generic import TemplateView
from groups.views import MyGroupListView
from django.views.generic import ListView
from django.contrib.auth.models import User
from accounts.models import UserProfileInfo


class HomeView(MyGroupListView):
    template_name = "home.html"

class ScoreBoardView(ListView):
    model = UserProfileInfo
    template_name = "score_board.html"
    ordering = ["-karma"]
