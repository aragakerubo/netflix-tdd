"""API routes for the catalog, registered on a DRF router."""

from rest_framework.routers import DefaultRouter

from .api import GenreViewSet, TitleViewSet

router = DefaultRouter()
router.register("titles", TitleViewSet, basename="title")
router.register("genres", GenreViewSet, basename="genre")

urlpatterns = router.urls
