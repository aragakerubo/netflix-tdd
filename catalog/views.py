from django.shortcuts import render

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
