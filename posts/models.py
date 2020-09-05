from django.db import models
from django.conf import settings
from groups.models import Group, GroupMembership
from django.utils import timezone
from django.db.models import Q, F
from django.urls import reverse
# Create your models here.

class Post(models.Model):
    group = models.ForeignKey(Group, related_name = "group_posts", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "my_posts", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, through = "PostVotes")
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        try:
            membership = GroupMembership.objects.filter(group = self.group).filter(person=self.author)
            if membership.exists():
                super().save(*args, **kwargs)  # Call the "real" save() method.
            else:
                print("could not save post because author does not belong to the group")
        except:
            print("some error occured while qurying GroupMembership table")

    def add_vote(self, vote):
        """
        Add vote to UpVotes if its value is 1 or to DownVotes if it is -1.
        """
        if vote == 1:
            self.up_votes +=1
            return self.up_votes
        elif vote == -1:
            self.down_votes +=1
            return self.down_votes
        else:
            print("wrong value")
            raise ValueError()

    def remove_vote(self, vote):
        """
        Remove vote from UpVotes if its value is 1 or from DownVotes if it is -1.
        """
        if vote == 1:
            self.up_votes -=1
            return self.up_votes
        elif vote == -1:
            self.down_votes -=1
            return self.down_votes
        else:
            print("wrong value")
            raise ValueError()


    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk':self.pk})

    class Meta:
        ordering = ['-created_at']

class PostVotes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote = models.IntegerField()

    class Meta:
        unique_together = ("post", "voter")

    def __str__(self):
        return self.voter.username + " has voted " + str(self.vote) + " for " + self.post.text
