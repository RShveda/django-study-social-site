from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length = 200, unique = True)
    slug = models.CharField(max_length = 200)
    description = models.TextField(max_length = 1000)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "own_groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through = "GroupMembership")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def get_absolute_url(self):
        return reverse('groups:group_detail', kwargs={'slug': self.slug})


class GroupMembership(models.Model):
    """
    Imntermediate model that connects User and Group
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("group", "person")

    def __str__(self):
        return self.person.username + " is a member of " + self.group.name
