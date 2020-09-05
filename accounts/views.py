from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import User
from groups.models import Group
from posts.models import Post
from accounts.models import UserProfileInfo

# Create your views here.

class UserCreateView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = UserCreationForm
    template_name = "signup.html"
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        profile = UserProfileInfo.objects.create(user=user, karma=0)
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, ListView):
    template_name = "profile.html"

    def get_queryset(self):
        try:
            post_author = User.objects.get(username = self.kwargs["username"])
            return Post.objects.filter(author=post_author)
        except:
            return Post.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all
        try:
            post_author = User.objects.get(username = self.kwargs["username"])
            context['group_list'] = Group.objects.filter(members = post_author)
        except:
            context['group_list'] = Group.objects.filter(members = self.request.user)
        return context
