from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        """Attach a convenience accessor for a user's saved titles.

        Adding a property to the User model here keeps templates and tests
        readable (user.watchlist_titles) without a custom user model.
        """
        from django.contrib.auth import get_user_model

        from .models import Title

        User = get_user_model()

        def watchlist_titles(self):
            return Title.objects.filter(watchlist_items__user=self)

        User.watchlist_titles = property(watchlist_titles)
