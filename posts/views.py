from django.shortcuts import render
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.views.generic import ListView
from .models import Post
from groups.models import Group
from django.urls import reverse_lazy, reverse

# Create your views here.
class MyPostListView(ListView):
    template_name = "my_post_list.html"
    def get_queryset(self):
        return Post.objects.filter(author = self.request.user)


class PostCreateView(CreateView):
    model = Post
    fields = ["text"]

    def get_success_url(self):
        group_slug = self.kwargs["group"]
        return reverse('groups:group_detail', kwargs={'slug': group_slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.group = Group.objects.get(slug = self.kwargs["group"])
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    fields = ["text"]
    success_url = "/"

    def get_success_url(self):
        group_slug = self.object.group.slug
        return reverse('groups:group_detail', kwargs={'slug': group_slug})


class PostDeleteView(DeleteView):
    model = Post

    def get_success_url(self):
        group_slug = self.object.group.slug
        return reverse_lazy('groups:group_detail', kwargs={'slug': group_slug})
