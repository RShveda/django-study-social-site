from django.test import TestCase, Client
from posts.models import Post
from django.contrib.auth.models import User
from groups.models import Group, GroupMembership
from django.urls import reverse

# Create your tests here.
class PostDeleteViewTests(TestCase):
        def setUp(self):
            client = Client()
            john = User.objects.create_user(username = "John", password = "newpass1234")
            bill = User.objects.create_user(username = "Bill", password = "newpass1234")
            new_group = Group.objects.create(name = "new_group",
                                            description = "some descriprion about the group",
                                            owner = john)
            new_group2 = Group.objects.create(name = "new_group2",
                                            description = "some descriprion about the group",
                                            owner = bill)
            GroupMembership.objects.create(group = new_group, person = bill)
            GroupMembership.objects.create(group = new_group2, person = bill)
            GroupMembership.objects.create(group = new_group, person = john)
            Post.objects.create(group=new_group, author=john, text = "post by john")
            Post.objects.create(group=new_group, author=john, text = "post by john 2")
            Post.objects.create(group=new_group, author=bill, text = "post by bill")

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
