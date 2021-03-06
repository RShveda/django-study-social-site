from django.shortcuts import render, redirect
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, PostVotes
from groups.models import Group, GroupMembership
from accounts.models import UserProfileInfo
from django.urls import reverse_lazy, reverse, resolve
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View

# Create your views here.
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["text"]

    def post(self, request, *args, **kwargs):
        """
        Only members of group can create posts.
        """
        person = self.request.user
        group = Group.objects.get(slug=self.kwargs["group"])
        try:
            membership = GroupMembership.objects.filter(group = group).filter(person=person)
            if membership.exists():
                return super().post(request, *args, **kwargs)
            else:
                messages.warning(request, '''Could not save post because you
                do not belong to the group. Please join group first''')
                return redirect(self.get_success_url())
        except:
            messages.warning(request, 'Somethin went wrong')
            return redirect(self.get_success_url())

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

    def post(self, request, *args, **kwargs):
        """
        Only authors can delete their posts.
        """
        self.object = self.get_object()
        if self.request.user == self.object.author:
            return super().post(request, *args, **kwargs)
        else:
            messages.warning(request, 'You cannot delete someone elses post')
            return redirect(self.request.path)

    def get_success_url(self):
        try:
            return self.request.POST["next"]
        except:
            group_slug = self.object.group.slug
            return reverse_lazy('groups:group_detail', kwargs={'slug': group_slug})

class PostVoteView(LoginRequiredMixin, View):
    """
    ViewClass that accepts post.pk as url kwarg and a "vote" value from POST request.
    Vote can be 1 or -1 integer. The vote is saved into PostVotes table, UpVotes(1)
    or DownVotes(-1) counter is incremented (using add_vote method), and karma for
    post author is updated by that value (1 or -1).
    """
    def post(self, request, **kwargs):
        post = Post.objects.get(pk = kwargs["pk"])
        voter = self.request.user
        vote = int(self.request.POST["vote"])
        try:
            post_vote = PostVotes.objects.create(post=post, voter=voter, vote=vote)
        except:
            messages.warning(request, 'Something went wrong')
        return redirect("groups:group_detail", slug=post.group.slug)

class PostRemoveVoteView(LoginRequiredMixin, View):
    """
    ViewClass that accepts post.pk as url kwarg and remove user vote for that post.
    First, the Vote value is retrieved from PostVote table so user karma and post vote
    counter (via remove_vote method) can be updated. After that PostVote object
    is deleted.
    """
    def post(self, request, **kwargs):
        post = Post.objects.get(pk = kwargs["pk"])
        voter = self.request.user
        try:
            post_vote = PostVotes.objects.get(post=post, voter=voter)
            post_vote.delete()
            messages.info(request, 'Vote removed successfully')
        except:
            messages.warning(request, 'something went wrong')
        return redirect("groups:group_detail", slug=post.group.slug)
