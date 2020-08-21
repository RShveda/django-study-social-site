from django.shortcuts import render
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post
from groups.models import Group
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["text"]

    def get_success_url(self):
        group_slug = self.kwargs["group"]
        return reverse('groups:group_detail', kwargs={'slug': group_slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.group = Group.objects.get(slug = self.kwargs["group"])
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["text"]

    def get_success_url(self):
        group_slug = self.object.group.slug
        return reverse('groups:group_detail', kwargs={'slug': group_slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post

    def get_success_url(self):
        group_slug = self.object.group.slug
        return reverse_lazy('groups:group_detail', kwargs={'slug': group_slug})
