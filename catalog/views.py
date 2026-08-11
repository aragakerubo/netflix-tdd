from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Genre, Title, WatchlistItem
from .models import Genre, Title


class SignupView(CreateView):
    """Let a visitor create an account, then send them to log in."""

    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


def home(request):
    query = request.GET.get("q", "").strip()
    media = request.GET.get("media", "").strip()

    titles = Title.objects.all()
    if query:
        titles = titles.filter(name__icontains=query)
    if media in Title.MediaType.values:
        titles = titles.filter(media_type=media)

    return render(
        request,
        "catalog/home.html",
        {"titles": titles, "query": query, "media": media},
    )


def title_detail(request, slug):
    title = get_object_or_404(Title, slug=slug)
    in_watchlist = (
        request.user.is_authenticated
        and WatchlistItem.objects.filter(user=request.user, title=title).exists()
    )
    return render(
        request,
        "catalog/title_detail.html",
        {"title": title, "in_watchlist": in_watchlist},
    )


def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    titles = genre.titles.all()
    return render(
        request,
        "catalog/genre_detail.html",
        {"genre": genre, "titles": titles},
    )


def title_watch(request, slug):
    """Play a title's trailer. 404s when no trailer is available."""
    title = get_object_or_404(Title, slug=slug)
    if not title.has_trailer:
        raise Http404("No trailer available for this title.")
    return render(request, "catalog/title_watch.html", {"title": title})


@login_required
def watchlist(request):
    """The signed-in user's saved titles."""
    titles = request.user.watchlist_titles
    return render(request, "catalog/watchlist.html", {"titles": titles})


@login_required
def watchlist_add(request, slug):
    """Save a title. Idempotent, so adding twice is harmless."""
    title = get_object_or_404(Title, slug=slug)
    WatchlistItem.objects.get_or_create(user=request.user, title=title)
    return redirect(title.get_absolute_url())


@login_required
def watchlist_remove(request, slug):
    """Remove a title from the user's list."""
    title = get_object_or_404(Title, slug=slug)
    WatchlistItem.objects.filter(user=request.user, title=title).delete()
    return redirect(title.get_absolute_url())


def healthz(request):
    """Liveness probe for deploy platforms and uptime checks."""
    return JsonResponse({"status": "ok"})
