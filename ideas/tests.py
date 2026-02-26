from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Idea, Comment, Vote


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech", slug="tech")

    def test_str(self):
        self.assertEqual(str(self.category), "Tech")


class IdeaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.category = Category.objects.create(name="Tech", slug="tech")
        self.idea = Idea.objects.create(
            title="Test Idea",
            slug="test-idea",
            author=self.user,
            category=self.category,
            summary="A short summary",
            description="Detailed description",
        )

    def test_str(self):
        self.assertEqual(str(self.idea), "Test Idea")

    def test_vote_count_zero(self):
        self.assertEqual(self.idea.vote_count(), 0)

    def test_comment_count_zero(self):
        self.assertEqual(self.idea.comment_count(), 0)

    def test_has_voted_false_for_unauthenticated(self):
        from django.contrib.auth.models import AnonymousUser
        anon = AnonymousUser()
        self.assertFalse(self.idea.has_voted(anon))

    def test_has_voted_after_voting(self):
        Vote.objects.create(idea=self.idea, user=self.user)
        self.assertTrue(self.idea.has_voted(self.user))


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voter", password="pass1234")
        self.idea = Idea.objects.create(
            title="Vote Test",
            slug="vote-test",
            author=self.user,
            summary="Summary",
            description="Desc",
        )

    def test_unique_vote_per_user(self):
        Vote.objects.create(idea=self.idea, user=self.user)
        with self.assertRaises(Exception):
            Vote.objects.create(idea=self.idea, user=self.user)


class IdeaListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="u1", password="pass1234")
        self.idea = Idea.objects.create(
            title="Visible Idea",
            slug="visible-idea",
            author=self.user,
            summary="Summary",
            description="Desc",
            status=Idea.STATUS_PUBLISHED,
        )

    def test_idea_list_returns_200(self):
        response = self.client.get(reverse("idea_list"))
        self.assertEqual(response.status_code, 200)

    def test_idea_list_shows_published_idea(self):
        response = self.client.get(reverse("idea_list"))
        self.assertContains(response, "Visible Idea")

    def test_trending_returns_200(self):
        response = self.client.get(reverse("trending"))
        self.assertEqual(response.status_code, 200)

    def test_search_filters_results(self):
        response = self.client.get(reverse("idea_list") + "?q=Visible")
        self.assertContains(response, "Visible Idea")

    def test_search_no_results(self):
        response = self.client.get(reverse("idea_list") + "?q=nonexistent123")
        self.assertNotContains(response, "Visible Idea")


class IdeaDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="author", password="pass1234")
        self.idea = Idea.objects.create(
            title="Detail Idea",
            slug="detail-idea",
            author=self.user,
            summary="Summary",
            description="Desc",
            status=Idea.STATUS_PUBLISHED,
        )

    def test_detail_returns_200(self):
        response = self.client.get(reverse("idea_detail", args=["detail-idea"]))
        self.assertEqual(response.status_code, 200)

    def test_detail_shows_title(self):
        response = self.client.get(reverse("idea_detail", args=["detail-idea"]))
        self.assertContains(response, "Detail Idea")

    def test_detail_404_for_draft(self):
        draft = Idea.objects.create(
            title="Draft Idea",
            slug="draft-idea",
            author=self.user,
            summary="s",
            description="d",
            status=Idea.STATUS_DRAFT,
        )
        response = self.client.get(reverse("idea_detail", args=["draft-idea"]))
        self.assertEqual(response.status_code, 404)


class IdeaCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="creator", password="pass1234")

    def test_create_requires_login(self):
        response = self.client.get(reverse("idea_create"))
        self.assertRedirects(response, "/accounts/login/?next=/submit/")

    def test_create_idea_post(self):
        self.client.login(username="creator", password="pass1234")
        response = self.client.post(reverse("idea_create"), {
            "title": "New Idea",
            "summary": "Short summary",
            "description": "Full description",
            "status": Idea.STATUS_PUBLISHED,
        })
        self.assertEqual(Idea.objects.filter(author=self.user).count(), 1)


class UpvoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="upvoter", password="pass1234")
        self.idea = Idea.objects.create(
            title="Upvote Idea",
            slug="upvote-idea",
            author=self.user,
            summary="s",
            description="d",
            status=Idea.STATUS_PUBLISHED,
        )

    def test_upvote_requires_login(self):
        response = self.client.post(reverse("upvote", args=["upvote-idea"]))
        self.assertEqual(response.status_code, 302)

    def test_upvote_toggles(self):
        self.client.login(username="upvoter", password="pass1234")
        response = self.client.post(reverse("upvote", args=["upvote-idea"]))
        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertTrue(data["voted"])
        self.assertEqual(data["vote_count"], 1)

        response2 = self.client.post(reverse("upvote", args=["upvote-idea"]))
        data2 = json.loads(response2.content)
        self.assertFalse(data2["voted"])
        self.assertEqual(data2["vote_count"], 0)


class CommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="commenter", password="pass1234")
        self.idea = Idea.objects.create(
            title="Comment Idea",
            slug="comment-idea",
            author=self.user,
            summary="s",
            description="d",
            status=Idea.STATUS_PUBLISHED,
        )

    def test_add_comment_requires_login(self):
        response = self.client.post(reverse("add_comment", args=["comment-idea"]), {"body": "Hello"})
        self.assertEqual(response.status_code, 302)

    def test_add_comment_logged_in(self):
        self.client.login(username="commenter", password="pass1234")
        self.client.post(reverse("add_comment", args=["comment-idea"]), {"body": "Great idea!"})
        self.assertEqual(Comment.objects.filter(idea=self.idea).count(), 1)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())
