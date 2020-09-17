from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from groups.models import Group, GroupMembership
from posts.models import Post, PostVotes
from accounts.models import UserProfileInfo


# Create your tests here.

class SignupViewTests(TestCase):
    def test_signup_template_rendered(self):
        """
        The page is rendered upon user request.
        """
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signup_form_success(self):
        """
        After successful signup new user will be created and the view will
        redirect (via HttpResponseRedirect) to a '/'.
        """
        response = self.client.post('/accounts/signup/', {'username': 'John', 'password1': 'smith1234', 'password2': 'smith1234'})
        self.assertTrue(User.objects.get(username="John"))
        self.assertEqual(response.url, "/")

class ProfileViewTests(TestCase):
    def setUp(self):
        client = Client()
        john = User.objects.create_user(username = "John", password = "newpass1234")
        bill = User.objects.create_user(username = "Bill", password = "newpass1234")
        john_profile = UserProfileInfo.objects.create(user=john)
        bill_profile = UserProfileInfo.objects.create(user=bill)
        new_group = Group.objects.create(name = "new_group",
                                        description = "some descriprion about the group",
                                        owner = john)
        new_group2 = Group.objects.create(name = "new_group2",
                                        description = "some descriprion about the group",
                                        owner = bill)
        new_group3 = Group.objects.create(name = "new_group3",
                                        description = "some descriprion about the group",
                                        owner = bill)
        GroupMembership.objects.create(group = new_group, person = bill)
        GroupMembership.objects.create(group = new_group2, person = bill)
        GroupMembership.objects.create(group = new_group, person = john)
        GroupMembership.objects.create(group = new_group3, person = john)
        post1 = Post.objects.create(group=new_group, author=john, text = "post by john")
        post2 = Post.objects.create(group=new_group, author=john, text = "post by john 2")
        post3 = Post.objects.create(group=new_group, author=bill, text = "post by bill")
        vote1_post1 = PostVotes.objects.create(post=post1, voter=john, vote=1)

    def test_open_profile_unauthorized(self):
        """
        User need to be logged to see the page, otherwise the view should redirect
        to Login page.
        """
        response = self.client.get('/accounts/my_profile/')
        self.assertRedirects(response, reverse("accounts:login")+"?next=/accounts/my_profile/")

    def test_render_self_profile_for_authorized_user(self):
        """
        My Profile page is rendered for logged user.
        """
        self.client.login(username = "John", password = "newpass1234")
        response = self.client.get('/accounts/my_profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile.html', response.template_name)
        my_post = Post.objects.get(text="post by john")
        self.assertIn(my_post, response.context["post_list"])

    def test_render_other_user_profile(self):
        """
        Loged User1 (john) will see User2 (bill) posts and groups when open
        User2 profile page.
        """
        self.client.login(username = "John", password = "newpass1234")
        response = self.client.get(reverse("accounts:profile", kwargs = {"username":"Bill"}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile.html', response.template_name)
        bill = User.objects.get(username="Bill")
        self.assertEqual(list(bill.group_set.all()), list(response.context["group_list"]))
        self.assertEqual(response.context["post_list"][0].text, "post by bill")

    def test_open_profile_page_via_url(self):
        """
        Profile page is rendered for logged user via accessing URL with following
        pattern: '/accounts/profile/<username>/'.
        """
        self.client.login(username = "John", password = "newpass1234")
        response = self.client.get('/accounts/profile/Bill/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile.html', response.template_name)
        self.assertEqual(response.context["post_list"][0].text, "post by bill")
