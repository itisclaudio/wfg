from dish.files.models import Dish
from django import template
from dish import settings #To call MEDIA_URL

register = template.Library()

@register.inclusion_tag('sidelatestdishes.html')

def show_dishes():
	## Trying to improve query, using photos doesn't work because when the dish has no photo, it doesn't show. 
	## Think a why to include favphoto in query
	#dishes_list_id = Dish.objects.filter(active=True).values_list('id', flat=True).order_by('-datetime')[:4]
	#photos = Picture.objects.filter(active=1, dish__pk__in = dishes_list_id).select_related('dish','owner__user').prefetch_related('dish__cuisines').order_by('-datetime')[:4]
	dish = Dish.objects.filter(active=True).prefetch_related('cuisines').select_related('userprofile__user').order_by('-datetime')[:4]
	return {'latest_dishes': dish,'LOADING_IMG':settings.LOADING_IMG}
	