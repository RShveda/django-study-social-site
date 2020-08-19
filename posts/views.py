from django.shortcuts import render
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post
from groups.models import Group
from django.urls import reverse_lazy, reverse

# Create your views here.
class MyPostListView(LoginRequiredMixin, ListView):
    template_name = "my_post_list.html"
    def get_queryset(self):
        return Post.objects.filter(author = self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all
        context['group_list'] = Group.objects.filter(members = self.request.user)
        return context


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
