from django import template
from django.conf import settings

from theme.utils import oebl_persons
from apis_core.apis_entities.models import Institution, Place, Person
from apis_core.apis_metainfo.models import Collection
register = template.Library()


@register.simple_tag
def people_count():
    col = getattr(settings, 'APIS_OEBL_BIO_COLLECTION', 'ÖBL Biographie')
    col1 = Collection.objects.filter(name=col)
    if col1.count() == 1:
        return Person.objects.filter(collection=col1[0]).count()
    else:
        return Person.objects.all().count()


@register.simple_tag
def institution_count():
    return Institution.objects.all().count()


@register.simple_tag
def place_count():
    return Place.objects.all().count()


@register.simple_tag
def formated_daterange(startdate, enddate):
    rangestring = ''
    if (startdate and startdate is not None) or (enddate and enddate is not None):
        rangestring += '('
        if (startdate and startdate is not None):
            rangestring += startdate
        if (enddate and enddate is not None):
            rangestring += '-' + enddate
        rangestring += ')'
    return rangestring

    