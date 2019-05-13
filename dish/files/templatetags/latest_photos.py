from dish.files.models import Picture
from django import template

register = template.Library()

@register.inclusion_tag('latestphotos.html')

def show_photos():
	photo = Picture.objects.filter(active=1).select_related('dish','owner__user').order_by('-datetime')[:4]
	return {'latest_photos': photo}
