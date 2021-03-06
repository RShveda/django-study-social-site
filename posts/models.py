from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from groups.models import Group, GroupMembership
from posts.mentions_helper import MentionsHandler as mentions
import markdown


class Post(models.Model):
    group = models.ForeignKey(Group, related_name = "group_posts", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "my_posts", on_delete=models.CASCADE)
    text = models.TextField()
    text_html = models.TextField(default="")
    created_at = models.DateTimeField(default=timezone.now)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, through = "PostVotes")
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        Only members can create post in a group.
        """
        text_with_mentions = mentions.check_for_mentions(self.text)
        self.text_html = markdown.markdown(text_with_mentions)
        try:
            membership = GroupMembership.objects.filter(group = self.group).filter(person=self.author)
            if membership.exists():
                super().save(*args, **kwargs)
            else:
                print("could not save post because author does not belong to the group")
        except:
            print("some error occurred while querying GroupMembership table")

    def add_vote(self, vote):
        """
        Add vote to UpVotes if its value is 1 or to DownVotes if it is -1.
        """
        if vote == 1:
            self.up_votes += 1
            return self.up_votes
        elif vote == -1:
            self.down_votes += 1
            return self.down_votes
        else:
            print("wrong value")
            raise ValueError("wrong value")

    def remove_vote(self, vote):
        """
        Remove vote from UpVotes if its value is 1 or from DownVotes if it is -1.
        """
        if vote == 1:
            self.up_votes -= 1
            return self.up_votes
        elif vote == -1:
            self.down_votes -= 1
            return self.down_votes
        else:
            print("wrong value")
            raise ValueError("wrong value")

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']


class PostVotes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.IntegerField()

    class Meta:
        unique_together = ("post", "voter")

    def save(self, *args, **kwargs):
        """
        When PostVote is saved Post(up_votes/down_votes) and UserProfileInfo(karma)
        tables are updated.
        """
        self.post.add_vote(self.vote)
        self.post.save()
        self.post.author.userprofileinfo.update_karma(self.vote)
        self.post.author.userprofileinfo.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        When PostVote is deleted Post(up_votes/down_votes) and UserProfileInfo(karma)
        tables are updated.
        """
        self.post.remove_vote(self.vote)
        self.post.save()
        self.post.author.userprofileinfo.update_karma(0-(self.vote))
        self.post.author.userprofileinfo.save()
        super().delete(*args, **kwargs)

    @receiver(pre_delete)
    def delete_on_cascade(sender, *args, **kwargs):
        """
        If PostVote is delete due to Group/Post deletion this method will update
        karma for post author.
        """
        if sender == Post:
            post = kwargs["instance"]
            for post_vote in post.postvotes_set.all():
                vote = post_vote.vote
                post_vote.post.author.userprofileinfo.update_karma(0-(vote))
                post_vote.post.author.userprofileinfo.save()

    def __str__(self):
        return self.voter.username + " has voted " + str(self.vote) + " for " + self.post.text
