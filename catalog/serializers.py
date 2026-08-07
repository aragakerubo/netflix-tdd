"""Serializers turning catalog models into JSON for the API."""

from rest_framework import serializers

from .models import Genre, Title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name", "slug"]


class TitleSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = [
            "name",
            "slug",
            "description",
            "year",
            "media_type",
            "runtime",
            "rating",
            "poster_path",
            "backdrop_path",
            "tmdb_id",
            "genres",
        ]
