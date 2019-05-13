from dish.files.models import Picture
from django import template

register = template.Library()

@register.inclusion_tag('latestphoto_user.html')

def show_photo_user(user):
	photos_user = Picture.objects.filter(active=1, owner=user.id).select_related('dish').order_by('-datetime')[:4]
	#dishesUser = Food.objects.filter(userprofile=user.id).order_by('-datetime')[:6]
	return {'latest_photos_user': photos_user}
