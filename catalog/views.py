from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Genre, Title


class SignupView(CreateView):
    """Let a visitor create an account, then send them to log in."""

    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


def home(request):
    query = request.GET.get("q", "").strip()
    if query:
        titles = Title.objects.filter(name__icontains=query)
    else:
        titles = Title.objects.all()
    return render(
        request,
        "catalog/home.html",
        {"titles": titles, "query": query},
    )


def title_detail(request, slug):
    title = get_object_or_404(Title, slug=slug)
    return render(request, "catalog/title_detail.html", {"title": title})


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


def healthz(request):
    """Liveness probe for deploy platforms and uptime checks."""
    return JsonResponse({"status": "ok"})
