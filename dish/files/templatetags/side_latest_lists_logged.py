from dish.files.models import List, userProfile
from django.db.models import Q
from django import template

register = template.Library()

@register.inclusion_tag('side_latestlists.html')

def show_lists(user):
	print user
	req_profile = userProfile.objects.get(user=user)
	lists = List.objects.filter(active=True).prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner').order_by('-modified')
	lists = lists.exclude(~Q(owner = req_profile), type = '3')[:5]
	list_count = lists.count()
	return {'latest_lists': lists,'list_count':list_count}
