from dish.files.models import List
from django import template

register = template.Library()

@register.inclusion_tag('side_latestlists.html')

def show_lists():
	lists = List.objects.filter(active=True).exclude(type = '3').prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner').order_by('-modified')[:5]
	#lists = List.objects.filter(active=True).exclude(type = '3').prefetch_related('dishes','listlikes').select_related('owner').order_by('-modified')[:5]
	#for list in lists:
	#dishes= ListDish.objects.filter(list=list).select_related('list','dish','owner__user').prefetch_related('dish__cuisines').order_by('index')
	list_count = lists.count()
	return {'latest_lists': lists,'list_count':list_count}
