from django.test import TestCase, Client
from posts.models import Post
from django.contrib.auth.models import User
from groups.models import Group, GroupMembership
from django.urls import reverse

# Create your tests here.
class SetTestCase(TestCase):
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


class GroupDeleteViewTest(SetTestCase):
    def test_delete_view_redirect_anauth_users_to_login_page(self):
        """
        Only logged users can access the page. Others should be redirected
        to login page.
        """
        response = self.client.get('/groups/new_group/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_author_delete_group(self):
        """
        Group get removed from DB by its owner after POST request to the view.
        """
        self.client.login(username = "John", password = "newpass1234")
        response = self.client.post('/groups/new_group/delete/')
        self.assertEqual(list(Group.objects.filter(slug="new_group")), [])

    def test_not_author_delete_group(self):
        """
        Group does not get removed from DB if POST request to the view is made
        by non author user.
        """
        self.client.login(username = "Bill", password = "newpass1234")
        response = self.client.post('/groups/new_group/delete/')
        self.assertNotEqual(list(Group.objects.filter(slug="new_group")), [])


class GroupUpdateViewTest(SetTestCase):
    def test_update_view_redirect_anauth_users_to_login_page(self):
        """
        Only logged users can access the page. Others should be redirected
        to login page.
        """
        response = self.client.get('/groups/new_group/edit/')
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_owner_edit_group(self):
        """
        Group get edited by its owner after POST request to the view.
        """
        self.client.login(username = "John", password = "newpass1234")
        response = self.client.post('/groups/new_group/edit/', {"name":"new_group4", "description":"some descr"})
        self.assertNotEqual(list(Group.objects.filter(name="new_group4")), [])

    def test_not_author_delete_group(self):
        """
        Group cannot be edited if POST request to the view is made
        by non author user.
        """
        self.client.login(username = "Bill", password = "newpass1234")
        response = self.client.post('/groups/new_group/edit/', {"name":"new_group4", "description":"some descr"})
        self.assertEqual(list(Group.objects.filter(slug="new_group4")), [])
