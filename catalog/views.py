from django.shortcuts import get_object_or_404, render

from .models import Title


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
