from django.contrib import admin
from .models import Category, Idea, Comment, Vote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "status", "created_at", "vote_count"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "summary", "description"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "created_at"

    def vote_count(self, obj):
        return obj.vote_count()
    vote_count.short_description = "Votes"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "idea", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["body"]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["user", "idea", "created_at"]
