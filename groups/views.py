from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Group, GroupMembership
from django.urls import reverse_lazy
from django.http import HttpResponse
# Create your views here.

class GroupListView(ListView):
    model = Group

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        form.instance.members.add(self.request.user)
        return super().form_valid(form)

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ["name", "description"]

class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('groups:group_list')

class GroupDetailView(DetailView):
    model = Group

class MyGroupListView(ListView):
    template_name = "my_group_list.html"
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Group.objects.filter(members = self.request.user)
        else:
            return None

class GroupJoinView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        group = Group.objects.get(slug = kwargs["slug"])
        person = self.request.user
        membership = GroupMembership.objects.create(group=group, person=person)
        membership.save()
        return redirect("groups:group_detail", slug=group.slug)
