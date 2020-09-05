from django.contrib import admin
from .models import Post, PostVotes
# Register your models here.
admin.site.register(Post)
admin.site.register(PostVotes)
