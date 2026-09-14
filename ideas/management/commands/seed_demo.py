from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from ideas.models import Category, Idea, Comment, Vote
import random

CATEGORIES = {
    "Fintech": "Payments, wallets, and financial tools",
    "EdTech": "Learning platforms and education tools",
    "HealthTech": "Health, fitness, and wellness",
    "AI & Data": "AI-powered products and data tools",
    "AgriTech": "Farming and food supply innovation",
}

IDEAS = [
    ("CampusBites", "Fintech", "Cashless meal credits for university students",
     "A prepaid wallet parents can top up that only works at verified campus vendors, with weekly spending reports."),
    ("LectureLoop", "EdTech", "AI summaries of every lecture",
     "Upload a recording, get chaptered notes, flashcards, and a practice quiz within minutes."),
    ("MediQueue", "HealthTech", "See real hospital wait times before you go",
     "Crowdsourced and clinic-reported wait times so patients choose the fastest nearby option."),
    ("FarmFleet", "AgriTech", "Tractor sharing for smallholder farmers",
     "Book unused tractors from nearby farms during planting season, splitting costs across co-ops."),
    ("ReceiptRadar", "Fintech", "Auto-track business expenses from photos",
     "Snap a receipt; AI extracts vendor, amount, and category, then exports a tax-ready report."),
    ("TutorTrail", "EdTech", "Peer tutoring marketplace with skill paths",
     "Students list subjects they can teach and want to learn; tutoring credits pay for lessons."),
    ("SleepSync", "HealthTech", "Sleep planner for shift workers",
     "Plans sleep windows around rotating rosters and silences notifications during core sleep."),
    ("MarketMind", "AI & Data", "Price forecasts for local market traders",
     "SMS-based predictions for staple goods so traders know what to stock and when to sell."),
]

DEMO_PASSWORD = "demo1234"


class Command(BaseCommand):
    help = "Seed the database with demo categories, ideas, votes and comments"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true",
                            help="Wipe existing ideas and reseed from scratch")

    def handle(self, *args, **options):
        if Idea.objects.exists() and not options["force"]:
            self.stdout.write(self.style.WARNING(
                "Ideas already exist. Run with --force to wipe and reseed."))
            return

        if options["force"]:
            Vote.objects.all().delete()
            Comment.objects.all().delete()
            Idea.objects.all().delete()
            Category.objects.all().delete()

        # Demo users (so votes/comments show real authors)
        users = []
        for name in ("alex", "sara", "mike"):
            user, _ = User.objects.get_or_create(username=name)
            user.set_password(DEMO_PASSWORD)
            user.save()
            users.append(user)

        # Categories
        cats = {}
        for name, desc in CATEGORIES.items():
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"description": desc, "slug": slugify(name)})
            cats[name] = cat

        # Ideas
        ideas = []
        for title, cat, summary, description in IDEAS:
            ideas.append(Idea.objects.create(
                title=title,
                slug=slugify(title),
                author=random.choice(users),
                category=cats[cat],
                summary=summary,
                description=description,
            ))

        # Votes and a comment on each idea
        for idea in ideas:
            for user in random.sample(users, k=random.randint(1, len(users))):
                Vote.objects.get_or_create(idea=idea, user=user)
            Comment.objects.get_or_create(
                idea=idea,
                author=random.choice(users),
                body="Love this — would use it immediately.",
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(ideas)} ideas, {Category.objects.count()} categories, with votes and comments."))