from datetime import date, timedelta

from django.conf import settings
from django.db.models import Q

from apis_core.apis_entities.models import Person
from apis_core.apis_labels.models import Label
from apis_core.apis_metainfo.models import Collection
from apis_core.apis_relations.models import PersonPlace
from apis_highlighter.highlighter import highlight_text_new

try:
    FEATURED_COLLECTION_NAME = settings.FEATURED_COLLECTION_NAME
except AttributeError:
    FEATURED_COLLECTION_NAME = None

try:
    BIRTH_REL_ID = settings.BIRTH_REL_ID
except AttributeError:
    BIRTH_REL_ID = None

try:
    DEATH_REL_ID = settings.DEATH_REL_ID
except AttributeError:
    DEATH_REL_ID = None

try:
    MAIN_TEXT = settings.MAIN_TEXT_NAME
except AttributeError:
    MAIN_TEXT = None


def get_main_text(MAIN_TEXT):
    if MAIN_TEXT is not None:
        return MAIN_TEXT
    else:
        return None


def enrich_person_context(person_object, context):
    if BIRTH_REL_ID is not None:
        try:
            context["place_of_birth"] = (
                PersonPlace.objects.filter(
                    related_person=person_object, relation_type_id=BIRTH_REL_ID
                )
                .first()
                .related_place
            )
        except AttributeError:
            context["place_of_birth"] = None
    else:
        context["place_of_birth"] = "Please define place of birth variable"
    if DEATH_REL_ID is not None:
        try:
            context["place_of_death"] = (
                PersonPlace.objects.filter(
                    related_person=person_object, relation_type_id=DEATH_REL_ID
                )
                .first()
                .related_place
            )
        except AttributeError:
            context["place_of_death"] = None
    else:
        context["place_of_death"] = "Please define place of death variable"
    try:
        context["profession"] = person_object.profession.all().last().name
    except AttributeError:
        context["profession"] = None
    try:
        if person_object.profession.all().count() > 1:
            context["profession_categories"] = person_object.profession.all()[
                : person_object.profession.all().count() - 1
            ]
    except AttributeError:
        context["profession_categories"] = None
    try:
        context[
            "related_places"
        ] = person_object.personplace_set.all().filter_for_user()
    except AttributeError:
        context["related_places"] = None
    try:
        context[
            "related_persons"
        ] = person_object.personperson_set.all().filter_for_user()
    except AttributeError:
        context["related_persons"] = None
    try:
        context[
            "related_institutions"
        ] = person_object.personinstitution_set.all().filter_for_user()
    except AttributeError:
        context["related_institutions"] = None
    haupttext = person_object.text.filter(
        kind__name=getattr(settings, "HAUPTTEXT_TEXT_NAME", "ÖBL Haupttext")
    )
    if haupttext.count() == 1:
        # context["haupttext"] = haupttext[0].text
        text = highlight_text_new(haupttext[0])
        context["haupttext"] = text[0]
    else:
        context["haupttext"] = "-"
    kurzinfo = person_object.text.filter(
        kind__name=getattr(settings, "KURZINFO_TEXT_NAME", "ÖBL Kurzinfo")
    )
    if kurzinfo.count() == 1:
        context["kurzinfo"] = kurzinfo[0].text
    else:
        context["kurzinfo"] = "-"
    wv = person_object.text.filter(
        kind__name=getattr(settings, "WERKVERZEICHNIS_TEXT_NAME", "ÖBL Werkverzeichnis")
    )
    if wv.count() == 1:
        context["werkverzeichnis"] = wv[0].text
    else:
        context["werkverzeichnis"] = False
    # dummy data für artikelversionen
    context["versionen"] = ["15.9.1995", "20.11.2004", "9.3.2021"]
    return context


def get_featured_person():
    if FEATURED_COLLECTION_NAME is not None:
        return Person.objects.filter(collection__name=FEATURED_COLLECTION_NAME).first()
    else:
        return None


col_oebl = getattr(settings, "APIS_OEBL_BIO_COLLECTION", "ÖBL Biographie")
col_oebl = Collection.objects.filter(name=col_oebl)
if col_oebl.count() == 1:
    oebl_persons = Person.objects.filter(collection=col_oebl[0])
else:
    oebl_persons = Person.objects.all()

# oebl_persons = Person.objects.exclude(Q(text=None) | Q(text__text=""))

oebl_persons_with_date = oebl_persons.exclude(Q(start_date=None) | Q(end_date=None))

person_place_born = PersonPlace.objects.filter(
    relation_type__name__icontains=getattr(settings, "BIRTH_REL_NAME", "birth")
)
person_place_death = PersonPlace.objects.filter(
    relation_type__name__icontains=getattr(settings, "DEATH_REL_NAME", "death")
)

current_date = date.today()
current_date = current_date - timedelta(days=1)
current_day = current_date.day
current_month = current_date.month


def get_born_range():
    oebl_persons_sorted_by_start_date = oebl_persons_with_date.order_by("start_date")
    oldest_person = oebl_persons_sorted_by_start_date.first()
    youngest_person = oebl_persons_sorted_by_start_date.last()
    return [oldest_person.start_date, youngest_person.start_date]


def get_died_range():
    oebl_persons_sorted_by_end_date = oebl_persons_with_date.order_by("end_date")
    person_died_first = oebl_persons_sorted_by_end_date.first()
    person_died_last = oebl_persons_sorted_by_end_date.last()
    return [person_died_first.end_date, person_died_last.end_date]


def get_died_latest():
    person_died_latest = oebl_persons.order_by("-end_date")[1]
    return person_died_latest.end_date


def get_daily_entries(context, qs):
    context["person_born"] = qs.filter(
        start_date__day=current_day, start_date__month=current_month
    )
    context["person_born_count"] = context["person_born"].count()
    context["person_died"] = qs.filter(
        end_date__day=current_day, end_date__month=current_month
    )
    context["person_died_count"] = context["person_died"].count()
    return context
