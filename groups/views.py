from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView
from .models import Group
from django.urls import reverse_lazy
# Create your views here.

class GroupListView(ListView):
    model = Group

class GroupCreateView(CreateView):
    model = Group
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        form.instance.members.add(self.request.user)
        return super().form_valid(form)

class GroupUpdateView(UpdateView):
    model = Group
    fields = ["name", "description"]

class GroupDeleteView(DeleteView):
    model = Group
    success_url = reverse_lazy('groups:group_list')

class GroupDetailView(DetailView):
    model = Group

class MyGroupListView(ListView):
    model = Group
    template_name = "my_group_list.html"
