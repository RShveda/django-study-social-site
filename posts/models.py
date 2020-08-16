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

    # TODO add http responce for non-existing memebership
    def save(self, *args, **kwargs):
        try:
            membership = GroupMembership.objects.filter(group = self.group).filter(person=self.author)
            if membership.exists():
                super().save(*args, **kwargs)  # Call the "real" save() method.
            else:
                print("could not save post because author does not belong to the group")
        except:
            print("some error occured while qurying GroupMembership table")


    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'pk':self.pk})
