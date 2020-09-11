from django import template
from posts.models import PostVotes

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def vote_value(value, arg):
    try:
        post_vote = PostVotes.objects.get(post=value, voter=arg)
        # print("yor vote is " + str(post_vote.vote))
        return post_vote.vote
    except:
        # print("error occured while trying to access user postvote")
        pass
