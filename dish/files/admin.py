from django.contrib import admin
from dish.files.models import (
	Cuisine, 
	Dish,
	DishSimilar,
	EmailQueue, 
	Feature, 
	Picture, 
	LikeDish, 
	LikePicture, 
	List, 
	ListDish, 
	LikeList, 
	SearchLog, 
	userProfile,
	)

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

UserAdmin.list_display = ('id','username', 'first_name', 'last_name','email', 'is_active', 'date_joined', 'is_staff')
UserAdmin.ordering = ('-id',)

class FeatureAdmin(admin.ModelAdmin):
	list_display = ['id','name','count']

class EmailQueueAdmin(admin.ModelAdmin):
	list_display = ['id','date','username','action','object','sent_flag']

class PictureAdmin(admin.ModelAdmin):
	list_display = ['id','urlname','likes','datetime','owner','likestot']
	list_filter = ['owner']
	search_fields = ['location']
	ordering = ('-id',)

class ListAdmin(admin.ModelAdmin):
	list_display = ['id','name','owner','created','type','likestot']
	list_filter = ['owner']
	search_fields = ['name']
	
class DishAdmin(admin.ModelAdmin):
	list_display = ['id','name_link','edit1','othernames','ingredients','short_date','short_description','urlname','likes','likestot']
	list_filter = ['userprofile','cuisines']
	search_fields = ['name']
	ordering = ('name',)
	def name_link(self, object):
		return '<a href="http://worldfood.guide/dish/'+object.urlname+'/" target="_blank">'+object.name+'</a>'
	name_link.allow_tags = True

	def edit1(self, object):
		return '<a href="http://worldfood.guide/dishedit/'+object.getid+'/" target="_blank">Edit</a>'
	edit1.allow_tags = True

	def short_date(self, object):
		return object.datetime.strftime("%d %b %Y")
		
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		print type(self)
		if db_field.name == "similars":
			#kwargs["queryset"] = Dish.objects.filter(id!=self.id)
			#kwargs["queryset"] = Dish.objects.all().exclude(pk=id)
			kwargs["queryset"] = Dish.objects.all()
		return super(DishAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
		
from django.db import models
class CuisineAdmin(admin.ModelAdmin):
	#list_display = ['id','name','num_food']
	search_fields = ['name','othernames','territory']
	list_display = ['id','name','othernames','territory','dishes_count','pictures_count','urlname','owner']
	ordering = ('-id',)

	def get_queryset(self, request):
		qs = super(CuisineAdmin, self).get_queryset(request)
		qs = qs.annotate(models.Count('dish'))
		return qs

	def dishes_count(self, obj):
		return obj.dish__count
	dishes_count.admin_order_field = 'dish__count'	

class ListDishAdmin(admin.ModelAdmin):
	list_display = ['id','index','list_plus','dish_plus']
	search_fields = ['list__name']
	def list_plus(self, object):
		return '('+str(object.list.id)+')-'+object.list.name[0:45]
	def dish_plus(self, object):
		return '('+str(object.dish.id)+')-'+object.dish.name
	
class LikePicture_Admin(admin.ModelAdmin):
	list_display = ['id','picture','url_name','profile','likes']
	list_filter = ['profile','picture']
	search_fields = ['picture__urlname']
	def url_name(self, object):
		return object.picture.urlname

class LikeList_Admin(admin.ModelAdmin):
	list_display = ['id','list','profile']
	list_filter = ['profile','list']

class DishSimilarAdmin(admin.ModelAdmin):
	list_display = ['id','dish1_urlname','dish2_urlname','profile','datetime']
	list_filter = ['profile','dish1']
	search_fields = ['dish1__urlname','dish2__urlname']
	def dish1_urlname(self, instance):
		return instance.dish1.urlname
	def dish2_urlname(self, instance):
		return instance.dish2.urlname
		
class LikeDish_Admin(admin.ModelAdmin):
	list_display = ['id','dish','url_name','profile','likes']
	list_filter = ['profile']
	search_fields = ['dish__urlname']
	def url_name(self, object):
		return object.dish.urlname

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "dish":
			kwargs["queryset"] = Dish.objects.all()
		if db_field.name == "profile":
			kwargs["queryset"] = userProfile.objects.all()
		return super(LikeDish_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ProfileAdmin(admin.ModelAdmin):
	list_display = ['id','user','user_email','firstname','lastname','photo']
	search_fields = ['user__username','user__email']
	ordering = ('-id',)
	def user_email(self, instance):
		return instance.user.email
	def lastname(self, instance):
		return instance.user.last_name
	def firstname(self, instance):
		return instance.user.first_name

class SearchLogAdmin(admin.ModelAdmin):
	list_display = ['datetime','searchwords','foodie','search_origin']
	#list_display = ['datetime','searchwords']
	search_fields = ['searchwords']
	ordering = ('-datetime',)
		
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(DishSimilar, DishSimilarAdmin)
admin.site.register(EmailQueue, EmailQueueAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(LikeDish, LikeDish_Admin)
admin.site.register(LikePicture, LikePicture_Admin)
admin.site.register(LikeList, LikeList_Admin)
admin.site.register(List, ListAdmin)
admin.site.register(ListDish, ListDishAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(SearchLog, SearchLogAdmin)
admin.site.register(userProfile, ProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)