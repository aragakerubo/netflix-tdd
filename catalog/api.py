"""Read-only API viewsets for the catalog."""

from rest_framework import viewsets

from .models import Genre, Title
from .serializers import GenreSerializer, TitleSerializer


class TitleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Title.objects.all().prefetch_related("genres")
    serializer_class = TitleSerializer
    lookup_field = "slug"


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = "slug"
