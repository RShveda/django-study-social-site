from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Group, GroupMembership
# Create your views here.

class GroupListView(ListView):
    model = Group

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save() #we need to save a group before assigning memebers via M2M
        form.instance.members.add(self.request.user)
        return super().form_valid(form)

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ["name", "description"]

    def post(self, request, *args, **kwargs):
        """
        Incapsulate ownership verification. Only group owner can edit the group.
        """
        self.object = self.get_object()
        if self.request.user == self.object.owner:
            return super().post(request, *args, **kwargs)
        else:
            messages.warning(request, 'You cannot edit someone elses group')
            return redirect(self.request.path)

class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('groups:group_list')

    def post(self, request, *args, **kwargs):
        """
        Incapsulate ownership verification. Only group owner can delete the group.
        """
        self.object = self.get_object()
        if self.request.user == self.object.owner:
            return super().post(request, *args, **kwargs)
        else:
            messages.warning(request, 'You cannot delete someone elses group')
            return redirect(self.request.path)

class GroupDetailView(DetailView):
    model = Group

class MyGroupListView(ListView):
    """
    This class is used as parent for HomePage View.
    TODO: move this class to main + remove my_group_list template and url.
    """
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
        try:
            membership = GroupMembership.objects.create(group=group, person=person)
            membership.save()
        except:
            messages.warning(request, 'You cannot join this group because you are already its member')
        return redirect("groups:group_detail", slug=group.slug)

class GroupLeaveView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        group = Group.objects.get(slug = kwargs["slug"])
        person = self.request.user
        try:
            membership = GroupMembership.objects.get(group=group, person=person)
            membership.delete()
            messages.info(request, 'Group abandoned successfully')
        except:
            messages.warning(request, 'Leaving group failed')
        return redirect("groups:group_detail", slug=group.slug)
