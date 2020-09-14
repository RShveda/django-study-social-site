from django.test import TestCase, Client
from posts.models import Post, PostVotes
from accounts.models import UserProfileInfo
from django.contrib.auth.models import User
from groups.models import Group, GroupMembership
from django.urls import reverse
from django.db import transaction, IntegrityError


class BaseTestSetup(TestCase):
    """
    Class with setup data to be used in tests.
    """
    def setUp(self):
        client = Client()
        john = User.objects.create_user(username = "John", password = "newpass1234")
        bill = User.objects.create_user(username = "Bill", password = "newpass1234")
        john_profile = UserProfileInfo.objects.create(user=john)
        new_group = Group.objects.create(name = "new_group",
                                        description = "some descriprion about the group",
                                        owner = john)
        new_group2 = Group.objects.create(name = "new_group2",
                                        description = "some descriprion about the group",
                                        owner = bill)
        GroupMembership.objects.create(group = new_group, person = bill)
        GroupMembership.objects.create(group = new_group2, person = bill)
        GroupMembership.objects.create(group = new_group, person = john)
        post1 = Post.objects.create(group=new_group, author=john, text = "post by john")
        post2 = Post.objects.create(group=new_group, author=john, text = "post by john 2")
        post3 = Post.objects.create(group=new_group, author=bill, text = "post by bill")
        vote1_post1 = PostVotes.objects.create(post=post1, voter=john, vote=1)



class PostDeleteViewTests(BaseTestSetup):
        def test_delete_view_redirect_anauth_users_to_login_page(self):
            """
            Only logged users can access the page. Others should be redirected
            to login page.
            """
            response = self.client.get('/posts/1/delete/')
            self.assertEqual(response.status_code, 302)
            self.assertIn("login", response.url)

        def test_author_delete_post(self):
            """
            Post get removed from DB by its owner after POST request to the view.
            """
            self.client.login(username = "John", password = "newpass1234")
            response = self.client.post('/posts/1/delete/')
            self.assertEqual(list(Post.objects.filter(id=1)), [])

        def test_not_author_delete_post(self):
            """
            Post does not get removed from DB if POST request to the view is made
            by non author user.
            """
            self.client.login(username = "Bill", password = "newpass1234")
            response = self.client.post('/posts/1/delete/', {"next":""})
            self.assertNotEqual(list(Post.objects.filter(id=1)), [])


        def test_delete_view_without_next_redirects_to_group_page(self):
            """
            By default, user will get redirected to a Group page after deletion
            of its post.
            """
            self.client.login(username = "John", password = "newpass1234")
            response = self.client.post('/posts/1/delete/')
            self.assertIn("group", response.url)

        def test_delete_view_with_next_redirects_to_my_profile(self):
            """
            If we delete post from user profile page, we will include next paramether
            to get redirected back to the profile page.
            """
            self.client.login(username = "John", password = "newpass1234")
            response = self.client.post('/posts/1/delete/', {"next":"?next=/accounts/my_profile/"})
            self.assertIn("profile", response.url)


class PostVoteViewTests(BaseTestSetup):
    def test_vote_view_allows_to_vote(self):
        """
        New record created in PostVotes table if user did note vote for that post
        in the past.
        """
        self.client.login(username = "John", password = "newpass1234")
        votes_len = len(PostVotes.objects.all())
        response = self.client.post('/posts/2/vote/', {"vote":"-1"})
        self.assertEqual(len(PostVotes.objects.all()), votes_len + 1)

    def test_vote_view_dont_allow_to_vote_multiple_times(self):
        """
        If user voted before for some post, the view will not add same record
        to DB.
        """
        self.client.login(username = "John", password = "newpass1234")
        votes_len = len(PostVotes.objects.all())
        try:
            with transaction.atomic():
                response1 = self.client.post('/posts/1/vote/', {"vote":"1"})
        except:
            pass
        self.assertEqual(len(PostVotes.objects.all()), votes_len)

    def test_vote_view_increment_up_vote_counter(self):
        """
        up_vote counter is incremented for the post that is voted on.
        """
        self.client.login(username = "John", password = "newpass1234")
        up_votes = Post.objects.get(id=2).up_votes
        response = self.client.post('/posts/2/vote/', {"vote":"1"})
        self.assertEqual(Post.objects.get(id=2).up_votes, up_votes + 1)

    def test_vote_view_increment_down_vote_counter(self):
        """
        down_vote counter is incremented for the post that is voted on.
        """
        self.client.login(username = "John", password = "newpass1234")
        down_votes = Post.objects.get(id=2).down_votes
        response = self.client.post('/posts/2/vote/', {"vote":"-1"})
        self.assertEqual(Post.objects.get(id=2).down_votes, down_votes + 1)

    def test_vote_view_update_author_karma(self):
        """
        Post author karma is updated depending on the vote.
        """
        self.client.login(username = "John", password = "newpass1234")
        user = User.objects.get(username="John")
        karma = UserProfileInfo.objects.get(user=user).karma
        response = self.client.post('/posts/2/vote/', {"vote":"-1"})
        self.assertEqual(UserProfileInfo.objects.get(user=user).karma, karma - 1)

class PostRemoveVoteView(BaseTestSetup):
    def test_remove_vote_view_allows_to_remove_vote(self):
        """
        Vote is removed from PostVotes tble.
        """
        self.client.login(username = "John", password = "newpass1234")
        votes_len = len(PostVotes.objects.all())
        response = self.client.post('/posts/1/remove_vote/')
        self.assertEqual(len(PostVotes.objects.all()), votes_len-1)

    def test_remove_vote_view_handles_none_existing_votes(self):
        """
        Cannot remove vote that does not exist. Instead of that app shows a message
        to user.
        """
        self.client.login(username = "John", password = "newpass1234")
        votes_len = len(PostVotes.objects.all())
        response = self.client.post('/posts/2/remove_vote/')
        redirect_response = self.client.get(response.url)
        messages = list(redirect_response.context['messages'])
        self.assertEqual('something went wrong', str(messages[0]))

    def test_remove_view_update_votes_counters(self):
        """
        up_votes (or down_votes) counter is updated if vote is removed.
        """
        self.client.login(username = "John", password = "newpass1234")
        up_votes = Post.objects.get(id=1).up_votes
        response = self.client.post('/posts/1/remove_vote/')
        self.assertEqual(Post.objects.get(id=1).up_votes, up_votes-1)

    def test_remove_view_update_author_karma(self):
        """
        Post author karma is updated after vote is removed.
        """
        self.client.login(username = "John", password = "newpass1234")
        user = User.objects.get(username="John")
        karma = UserProfileInfo.objects.get(user=user).karma
        response = self.client.post('/posts/1/remove_vote/')
        self.assertEqual(UserProfileInfo.objects.get(user=user).karma, karma - 1)
