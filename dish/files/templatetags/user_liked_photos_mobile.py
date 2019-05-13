from dish.files.models import Picture, LikePicture
from django import template

register = template.Library()

@register.inclusion_tag('user_liked_photos_mobile.html')

def show_liked_photos(user):
	photos = Picture.objects.filter(active = True, owner=user.id).select_related('owner__user').order_by('-likestot')[:5]
	return {'user_liked_photos_mobile': photos}

"""photos = Picture.objects.filter(active=1, owner=user.id).extra(
		select={
			'num_likes': 'SELECT COUNT(*) FROM files_likepicture WHERE files_likepicture.likes = TRUE AND files_picture.id = files_likepicture.picture_id',
			},
	).order_by('-num_likes')[:5]"""