from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Idea(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="ideas"
    )
    summary = models.TextField(help_text="A short summary of your idea (max 500 chars)", max_length=500)
    description = models.TextField(help_text="Describe your idea in detail")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def vote_count(self):
        return self.votes.count()

    def comment_count(self):
        return self.comments.count()

    def has_voted(self, user):
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()


class Comment(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.idea}"


class Vote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("idea", "user")

    def __str__(self):
        return f"{self.user} voted on {self.idea}"
