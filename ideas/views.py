from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Idea, Category, Comment, Vote
from .forms import IdeaForm, CommentForm, RegisterForm


def idea_list(request):
    ideas = Idea.objects.filter(status=Idea.STATUS_PUBLISHED).annotate(
        vote_count=Count("votes"), comment_count=Count("comments")
    )
    category_slug = request.GET.get("category")
    search = request.GET.get("q", "").strip()
    categories = Category.objects.all()
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        ideas = ideas.filter(category=selected_category)

    if search:
        ideas = ideas.filter(title__icontains=search) | ideas.filter(summary__icontains=search)

    ideas = ideas.order_by("-created_at")

    context = {
        "ideas": ideas,
        "categories": categories,
        "selected_category": selected_category,
        "search": search,
        "page_title": "All Ideas",
    }
    return render(request, "ideas/idea_list.html", context)


def trending(request):
    ideas = (
        Idea.objects.filter(status=Idea.STATUS_PUBLISHED)
        .annotate(vote_count=Count("votes"), comment_count=Count("comments"))
        .order_by("-vote_count", "-comment_count", "-created_at")
    )
    categories = Category.objects.all()
    context = {
        "ideas": ideas,
        "categories": categories,
        "selected_category": None,
        "search": "",
        "page_title": "Trending Ideas",
    }
    return render(request, "ideas/idea_list.html", context)


def idea_detail(request, slug):
    idea = get_object_or_404(Idea, slug=slug, status=Idea.STATUS_PUBLISHED)
    comments = idea.comments.select_related("author")
    has_voted = idea.has_voted(request.user)
    comment_form = CommentForm()

    context = {
        "idea": idea,
        "comments": comments,
        "has_voted": has_voted,
        "comment_form": comment_form,
        "vote_count": idea.vote_count(),
    }
    return render(request, "ideas/idea_detail.html", context)


@login_required
def idea_create(request):
    if request.method == "POST":
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            base_slug = slugify(idea.title)
            slug = base_slug
            counter = 1
            while Idea.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            idea.slug = slug
            idea.save()
            messages.success(request, "Your idea has been submitted!")
            return redirect("idea_detail", slug=idea.slug)
    else:
        form = IdeaForm()
    return render(request, "ideas/idea_form.html", {"form": form, "action": "Submit"})


@login_required
def idea_edit(request, slug):
    idea = get_object_or_404(Idea, slug=slug, author=request.user)
    if request.method == "POST":
        form = IdeaForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, "Your idea has been updated!")
            return redirect("idea_detail", slug=idea.slug)
    else:
        form = IdeaForm(instance=idea)
    return render(request, "ideas/idea_form.html", {"form": form, "action": "Update", "idea": idea})


@login_required
def idea_delete(request, slug):
    idea = get_object_or_404(Idea, slug=slug, author=request.user)
    if request.method == "POST":
        idea.delete()
        messages.success(request, "Your idea has been deleted.")
        return redirect("idea_list")
    return render(request, "ideas/idea_confirm_delete.html", {"idea": idea})


@login_required
@require_POST
def upvote(request, slug):
    idea = get_object_or_404(Idea, slug=slug, status=Idea.STATUS_PUBLISHED)
    vote, created = Vote.objects.get_or_create(idea=idea, user=request.user)
    if not created:
        vote.delete()
        voted = False
    else:
        voted = True
    return JsonResponse({"voted": voted, "vote_count": idea.vote_count()})


@login_required
@require_POST
def add_comment(request, slug):
    idea = get_object_or_404(Idea, slug=slug, status=Idea.STATUS_PUBLISHED)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.idea = idea
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added.")
    return redirect("idea_detail", slug=slug)


def register(request):
    if request.user.is_authenticated:
        return redirect("idea_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("idea_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def user_ideas(request, username):
    from django.contrib.auth.models import User as AuthUser
    author = get_object_or_404(AuthUser, username=username)
    ideas = Idea.objects.filter(author=author, status=Idea.STATUS_PUBLISHED).annotate(
        vote_count=Count("votes"), comment_count=Count("comments")
    )
    context = {
        "profile_user": author,
        "ideas": ideas,
    }
    return render(request, "ideas/user_ideas.html", context)
