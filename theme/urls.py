from django.urls import path, re_path

from . import dal_views
from . import views

app_name = "theme"


urlpatterns = [
    path(r"", views.IndexView.as_view(), name="start"),
    path(r"imprint/", views.ImprintView.as_view(), name="imprint"),
    path(r"about/", views.AboutView.as_view(), name="about"),
    path(r"contact/", views.ContactView.as_view(), name="contact"),
    path(r"expert-search/", views.PersonListView.as_view(), name="expert-search"),
    path(r"search/?", views.SearchView.as_view(), name="search"),
    re_path(
        r"^person/(?P<pk>[0-9]+)$",
        views.PersonDetailView.as_view(),
        name="person-detail",
    ),
    path(
        r"ac/obel-person/",
        dal_views.OeblPersons.as_view(),
        name="obel-person-autocomplete",
    ),
    path(
        r"ac/obel-professions/",
        dal_views.ProfessionAC.as_view(),
        name="obel-professions-autocomplete",
    ),
]
