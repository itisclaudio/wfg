# Create your models here.
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import os
from PIL import Image
from datetime import datetime
from django.db.models import Max
from dish import settings
from django.template.defaultfilters import truncatechars
from django.core.urlresolvers import reverse#used in get_absolute_url for sitemaps in models
from django.utils import timezone
from allauth.account.models import EmailAddress#For:django-allauth, for def account_verified(self): in userProfile

def generate_url(instance,filename):
	if not instance.pk:
		from django.db.models import Max
		getKey = userProfile.objects.aggregate(next=Max('id'))['next']
		if getKey >= 1:
			getKey = getKey+1
		else:
			getKey = 1
	else:
		getKey = instance.user.pk
	ext = filename.split('.')[-1]
	ruta = "users/%s.%s" %(str(getKey),ext.lower())
	return ruta

class EmailQueue(models.Model):
	##Stores information from element updates to be sent by email 
	date	= models.DateTimeField(default=timezone.now)
	username	= models.CharField(max_length=30, null=True ,blank=True)
	action	= models.CharField(max_length=30, null=True ,blank=True)
	object	= models.CharField(max_length=30, null=True ,blank=True)
	url_plus	= models.CharField(max_length=300, null=True ,blank=True)
	sent_flag	= models.BooleanField(default=False)
"""
class Emails(models.Model):
	##Stores general information to be sent by email 
	datetime	= models.DateTimeField(default=timezone.now)
	subject	= models.CharField(max_length=30, null=True ,blank=True)
	content = models.TextField(max_length=9500,blank=True)
	sent_flag	= models.BooleanField(default=False)
"""
	
class userProfile(models.Model):
	user        =   models.OneToOneField(User)
	photo       =   models.ImageField(upload_to=generate_url, null=True ,blank=True)
	telefono    =   models.CharField(max_length=30, null=True ,blank=True)
	about 		=	models.TextField(max_length=4000, null=True, blank=True)
	pass_backup =   models.CharField(max_length=30, null=True ,blank=True)
	uploads		=	models.IntegerField(null=True ,blank=True)
	names_show	= 	models.BooleanField(default=True)
	email_show	= 	models.BooleanField(default=True)
	only_social = 	models.BooleanField(default=False)#False = has password with WFG and maybe also with social, True=not password with WFG, only social
	#email_show	= 	models.NullBooleanField(null=True ,blank=True)

	#important for sitmaps:
	def get_absolute_url(self):
		return reverse('view_profile', kwargs={'username':self.user.username})

	def photolikes(self):
		#"Returns total number of photo likes"
		likes_tot = LikePicture.objects.filter(profile=self.id, likes=1).count()
		return likes_tot

	def photocount(self):
		#"Returns total number of photos by userProfile"
		return Picture.objects.filter(owner=self.id, active=True).count()
		
	def _get_photofilename(self):
		#"Returns file name with out extension"
		name, extension = os.path.splitext(self.photo.url)
		return name
	photofilename = property(_get_photofilename)

	def photofilename(self):
		name, extension = os.path.splitext(self.photo.url)
		return name

	def extension(self):
		name, extension = os.path.splitext(self.photo.url)
		#extension.replace("&amp;","&")
		return extension

	#django-allauth: method for email-verification status django-allauth
	def account_verified(self):
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False
		
	def save(self):
		if self.about:
			self.about = self.about.lstrip()
		#**************To resize main image
		if not self.photo:
			super(userProfile, self).save()
			return
		super(userProfile, self).save()

		#file_path = str(self.photo.path)#Gives problems when files is: Bánh rán.jpg
		file_path = self.photo.path.encode('utf-8')
		user_filename, ext = os.path.splitext(self.photo.name)
		image = Image.open(file_path)

		image.save(file_path)
		sizes = {'full': {'height': 500, 'width': 500}, 'medium': {'height': 250, 'width': 250},'thumbnail': {'height': 100, 'width': 100},}
		filename = user_filename.strip('users/')
		
		# create full image
		image.thumbnail((sizes['full']['width'], sizes['full']['height']), Image.ANTIALIAS)
		image.save(settings.UPLOAD_USER + '/' + filename+ext.lower())
		
		# create medium image
		image.thumbnail((sizes['medium']['width'], sizes['medium']['height']), Image.ANTIALIAS)
		image.save(settings.UPLOAD_USER + '/' + filename +"-med"+ext.lower())

		# create thumbnail
		image.thumbnail((sizes['thumbnail']['width'], sizes['thumbnail']['height']), Image.ANTIALIAS)
		image.save(settings.UPLOAD_USER + '/' + filename +"-thum"+ext.lower())
		
	def __unicode__(self):
		return self.user.username
		
	class Meta:
		ordering = ('user__username',)

class SearchLog(models.Model):
	##Stores search workds made by users 
	datetime	= models.DateTimeField(default=timezone.now)
	searchwords = models.TextField(max_length=99,blank=True)
	search_origin = models.CharField(max_length=300, null=True ,blank=True)
	foodie	= models.ForeignKey(userProfile, null=True ,blank=True)
		
class Feature(models.Model):
	#Dish feature: kisd friendly, spicy, vegan
	name		= models.CharField(max_length=50)
	description = models.TextField(max_length=9500,blank=True)
	icon		= models.CharField(max_length=30,blank=True)
	count		= models.IntegerField(null=True ,blank=True, default=0)
	def __unicode__(self):
		return self.name
		
class Cuisine(models.Model):
	name        = models.CharField(max_length=50)
	othernames = models.CharField(max_length=100,blank=True, verbose_name='Other names')
	territory = models.TextField(max_length=100, blank=True, null=True)
	description = models.TextField(max_length=9500,blank=True)
	owner = models.ForeignKey(userProfile, null=True)
	active = models.BooleanField(default=True)
	urlname     = models.CharField(max_length=80,blank=True)
	def _get_num_dishes(self):
		"Returns Q of dishes"
		num = Dish.objects.filter(cuisine__in=self.cuisine).count()
		return num
	num_dishes = property(_get_num_dishes)
	def __unicode__(self):
		return self.name

	#important for sitmaps:
	def get_absolute_url(self):
		#return reverse('cuisine_view', args=[str(self.urlname)])
		return reverse('view_cuisine', kwargs={'urlname':self.urlname})

	def _get_dishes(self):
		"Returns total number of dishes"
		dishes_tot = Dish.objects.filter(cuisines = self).count()
		return dishes_tot
	dishes_count = property(_get_dishes)
	
	def _get_pictures(self):
		"Returns total number of pictures"
		pictures_tot = Picture.objects.filter(dish__cuisines = self).count()
		return pictures_tot
	pictures_count = property(_get_pictures)

	def favphoto(self):
		#This is the picture from current cuisine with most likes, but not necesarily from the most liked dish
		favphoto = Picture.objects.filter(dish__cuisines=self.id).order_by('-likestot').first()
		#print "For "+str(self.name)+", favphoto: "+str(favphoto)
		return favphoto

	def favdish(self):
		favdish = Dish.objects.filter(cuisines=self.id).order_by('-likestot').first()
		return favdish

	class Meta:
		ordering = ('name',)
	
def pluralize(ingredient):
	INGREDIENTS_PLURAL_MAP = {
		'avocado': 'avocados',
		'bean': 'beans',
		'carrot': 'carrots',
		'cucumber': 'cucumbers',
		'chili': 'chillies',
		'egg': 'eggs',
		'eggplant': 'eggplants',
		'onion': 'onions',
		'mussel': 'mussels',
		'noodle': 'noodles',
		'potato': 'potatoes',
		'scallion': 'scallions',
		'scallop': 'scallops',
		'shrimp': 'shrimps',
		'tomato': 'tomatoes',
		'vegetable': 'vegetables',
		}
	if ingredient in INGREDIENTS_PLURAL_MAP:
		plural = INGREDIENTS_PLURAL_MAP.get(ingredient)
		return plural
	else:
		return ingredient

class Dish(models.Model):
	cuisines	= models.ManyToManyField(Cuisine, blank=True)
	features	= models.ManyToManyField(Feature, blank=True)
	userprofile = models.ForeignKey(userProfile)
	name        = models.CharField(max_length=75)
	urlname     = models.CharField(max_length=80)
	othernames	= models.CharField(max_length=200,blank=True, verbose_name='Other names')
	ingredients	= models.CharField(max_length=300,blank=True)
	description	= models.TextField(max_length=9500,blank=True)
	datetime	= models.DateTimeField(default=timezone.now)
	dishlikes	= models.ManyToManyField(userProfile, related_name='dishlikes', through='LikeDish', blank=True)
	likestot	= models.IntegerField(null=True ,blank=True, default=0)
	similars	= models.ManyToManyField('self', blank=True)
	similar		= models.ManyToManyField('self', symmetrical=False, related_name='similar_to', through='DishSimilar', blank=True)
	active		= models.BooleanField(default=True)
	photo_main	= models.CharField(max_length=80, null=True ,blank=True)

	def favphotomed(self):
		name, extension = os.path.splitext(self.photo_main)
		return "%s%s-med%s"%(settings.MEDIA_URL,name,extension)
	
	def favphotothum(self):
		name, extension = os.path.splitext(self.photo_main)
		return "%s%s-thum%s"%(settings.MEDIA_URL,name,extension)
	
	def filename(self):
		name, extension = os.path.splitext(self.photo_main)
		return name

	def extension(self):
		name, extension = os.path.splitext(self.photo_main)
		return extension
	
	#Method that receives True to increase like or False to decrease
	def like(self, like_val):
		if like_val:
			self.likestot += 1
		else:
			self.likestot -= 1
		self.save()
	
	##important for sitmaps:
	def get_absolute_url(self):
		return reverse('view_dish', kwargs={'urlname':self.urlname})

	#Used in: admin.py
	def get_id(self):
		return str(self.id)
	getid = property(get_id)

	def favphoto(self):
		#Returns the photo with most likes when photo.dish = dish
		#Used: cuisine.html, cuisines.html, side_latest_dishes
		favphoto = Picture.objects.filter(dish=self.id).order_by('-likestot').first()
		return favphoto

	def _get_likes(self):
		#Returns total number of likes
		likes_tot = LikeDish.objects.filter(dish=self.id, likes=1).count()
		return likes_tot
	likes = property(_get_likes)

	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ('name',)
		
	@property
	def short_description(self):
		return truncatechars(self.description,40)

	def save(self):
		self.name = self.name.strip()
		self.othernames = self.othernames.rstrip(',').strip()
		self.ingredients = self.ingredients.rstrip(',').strip()
		self.description = self.description.strip()
		if self.ingredients:
			pluralized_ingedient_list = []
			ingredients_list = self.ingredients.lower().split(',')
			ingredients_list = [line.strip() for line in ingredients_list]
			for i in ingredients_list:
				pluralized_i = pluralize(i)
				pluralized_ingedient_list.append(pluralized_i)
			self.ingredients = ', '.join(pluralized_ingedient_list)
		super(Dish, self).save()

class DishSimilar(models.Model):
	dish1		= models.ForeignKey(Dish, related_name='dish_origin')
	dish2		= models.ForeignKey(Dish, related_name='dish_similar')
	profile		= models.ForeignKey(userProfile)
	datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)
		
def picture_url(instance,filename):
	from django.db.models import Max
	getKey = Picture.objects.aggregate(next=Max('id'))['next']
	if getKey >= 1:
		getKey = getKey+1
	else:
		getKey = 1
	ext = filename.split('.')[-1]
	if settings.LOCAL_DEV:
		#return "dishes/%s_%s.%s" %(instance.dish.urlname,str(getKey),ext.lower())
		return "dishes/{}_{}.{}".format(instance.dish.urlname, str(getKey), ext.lower())
	else:
		return "dishes_original/{}_{}.{}".format(instance.dish.urlname,str(getKey),ext.lower())
		#return "dishes_original/%s_%s.%s" %(instance.dish.urlname,str(getKey),ext.lower())

class List(models.Model):
	TYPE_LIST = (('1', "Personal: Only owner can add dishes"),('2', "Public: Users can add dishes"),('3', "Private: Only owner can see it"),)
	name        = models.CharField(max_length=92, blank=False, null=False, verbose_name='List title')
	urlname     = models.CharField(max_length=100, blank=False, null=False)
	dishes 		= models.ManyToManyField(Dish, related_name='dishlist', through='ListDish', blank=True)
	description = models.TextField(max_length=9500,blank=True)
	owner 		= models.ForeignKey(userProfile)
	created		= models.DateTimeField(default=timezone.now)
	modified 	= models.DateTimeField(default=timezone.now)
	type 		= models.CharField(max_length=1, choices=TYPE_LIST, default='1')
	private 	= models.BooleanField(default=False)
	listlikes 	= models.ManyToManyField(userProfile, related_name='listlikes', through='LikeList', blank=True)
	likestot 	= models.IntegerField(null=True ,blank=True, default=0)
	active 		= models.BooleanField(default=True)
	
	#Method that receives True to increase like or False to decrease
	def like(self, like_val):
		if like_val:
			self.likestot += 1
		else:
			self.likestot -= 1
		self.save()
	
	def _get_num_dishes(self):
		"Returns Q of dishes"
		num = ListDish.objects.filter(list__in=self.id).count()
		return num
	num_dishes = property(_get_num_dishes)
	def __unicode__(self):
		return self.name

	#important for sitmaps:
	def get_absolute_url(self):
		return reverse('view_list', kwargs={'urlname':self.urlname})

	def _get_dishes(self):
		"Returns total number of dishes"
		dishes_tot = ListDish.objects.filter(list = self).count()
		return dishes_tot
	dishes_count = property(_get_dishes)

	def save(self):
		self.name = self.name.lstrip().rstrip()
		self.description = self.description.lstrip()
		super(List, self).save()

	def _get_likes(self):
		"Returns total number of likes"
		likes_tot = LikeList.objects.filter(list=self.id).count()
		return likes_tot
	likes = property(_get_likes)
		
	class Meta:
		ordering = ('-modified',)

class ListDish(models.Model):
	list		= models.ForeignKey(List)
	dish		= models.ForeignKey(Dish)
	description = models.TextField(max_length=1990,blank=True)
	index		= models.IntegerField(null=True ,blank=True)
	owner 		= models.ForeignKey(userProfile, null=True ,blank=True)
	def __unicode__(self):
		return "%s, %s"%(self.list,self.dish)
	class Meta:
		ordering = ('list','index')

def UpdateMainPhoto(id_dish):
	print "In: UpdateMainPhoto 2"
	dish = Dish.objects.get(pk=id_dish)
	favphoto = Picture.objects.filter(dish=dish.id).order_by('-likestot').first()
	if favphoto:
		## There is a photo, use obj
		dish.photo_main = str(favphoto.location)
	else:
		## There is no photo, clear photo_m
		dish.photo_main = ""
	dish.save()
#000		
class Picture(models.Model):
	#dish = models.ForeignKey(Dish, related_name='dishpicture')
	dish = models.ForeignKey(Dish)
	urlname = models.CharField(max_length=80, null=True ,blank=True)
	owner = models.ForeignKey(userProfile)
	piclikes = models.ManyToManyField(userProfile, related_name='piclikes', through='LikePicture', blank=True)
	location = models.ImageField(upload_to=picture_url)
	comments = models.CharField(max_length=400, blank=True, null=True)
	likestot = models.IntegerField(null=True ,blank=True, default=0)
	datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)
	active = models.BooleanField(default=True)
	ownit = models.BooleanField(default=True)
	creditsname = models.CharField(max_length=100, blank=True, null=True)
	creditsurl = models.CharField(max_length=2000, blank=True, null=True)

	#Method that receives True to increase like or False to decrease
	def like(self, like_val):
		if like_val:
			self.likestot += 1
		else:
			self.likestot -= 1
		self.save()
		
	def _get_likes(self):
		"Returns total number of likes"
		likes_tot = LikePicture.objects.filter(picture=self.id, likes=1).count()
		return likes_tot
	likes = property(_get_likes)

	def _get_file_name(self):
		"Returns file name with out extension"
		name, extension = os.path.splitext(self.location.url)
		return name
	file_name = property(_get_file_name)
	
	def _get_extension(self):
		"Returns file name with out extension"
		name, extension = os.path.splitext(self.location.url)
		return extension
	extension_name = property(_get_extension)

	#important for sitmaps:
	def get_absolute_url(self):
		return reverse('view_photourl', kwargs={'urlname':self.urlname})

	def filename(self):
		name, extension = os.path.splitext(self.location.url)
		return name

	def extension(self):
		name, extension = os.path.splitext(self.location.url)
		return extension

	def __unicode__(self):
		return "%s"%(self.urlname)
		
	def save(self):
		##** Done with lambda in AWS S3, Done manually localy
		if settings.LOCAL_DEV:
			#Test
			file = self.location.path.encode('utf-8')
			if os.path.exists(file):
				## No new file, renaming current file and thumbs
				filenamewhole = str(self.location)
				print filenamewhole
				filenamewhole = filenamewhole.replace("dishes/", "")
				filename, ext = os.path.splitext(filenamewhole)
				cad = settings.UPLOAD_DISH + '/'
				fileThum = cad+filename+'-thum'+ext
				fileMed = cad+filename+'-med'+ext
				fileReg = cad+filename+'-reg'+ext
				urlname = self.dish.urlname
				newname1 = cad+urlname+'_'+str(self.id)+ext
				newThum =  cad+urlname+'_'+str(self.id)+'-thum'+ext
				newMed =  cad+urlname+'_'+str(self.id)+'-med'+ext
				newReg =  cad+urlname+'_'+str(self.id)+'-reg'+ext
				if os.path.exists(file):
					os.rename(file, newname1)
				if os.path.exists(fileThum):
					os.rename(fileThum, newThum)
				if os.path.exists(fileMed):
					os.rename(fileMed, newMed)
				if os.path.exists(fileReg):
					os.rename(fileReg, newReg)
				self.urlname = urlname+'_'+str(self.id)
				self.location = 'dishes/'+urlname+'_'+str(self.id)+ext
				#pic.save()
				super(Picture, self).save()
				return
			print "New file, create thumbs"
			## Uploading new file, creating thumbs
			super(Picture, self).save()
			
			p_w = self.location.width
			p_h = self.location.height
			
			filename = str(self.location.path)
			image = Image.open(filename)
			ext = filename.split('.')[-1]

			sizes={'thum':{'h':100,'w':100},'med':{'h':400,'w':400},'reg':{'h':800,'w':800},'max':{'h':1200,'w':1200},}
			
			# create "max-size" image
			if any ((p_w < sizes['max']['w'], p_h < sizes['max']['h'])):#User resize and not thumdnail to make it bigger
				if p_h > p_w:
					max_wsize = int(sizes['max']['h']*p_w/p_h)
					#print "Max resize, W: "+str(max_wsize)+" H:"+str(sizes['max']['h'])
					image_new = image.resize((max_wsize,int(sizes['max']['h'])), Image.ANTIALIAS)
					image_new.save(filename)
				else:
					max_hsize = int(p_h*sizes['max']['w']/p_w)
					image_new = image.resize((int(sizes['max']['w']),max_hsize), Image.ANTIALIAS)
					image_new.save(filename)
			else:
				image.thumbnail((sizes['max']['w'], sizes['max']['h']), Image.ANTIALIAS)
				image.save(filename)
			
			# create "Reg-size" image
			image.thumbnail((sizes['reg']['w'], sizes['reg']['h']), Image.ANTIALIAS)
			image.save(settings.UPLOAD_DISH + '/' +self.urlname+"-reg."+ext.lower())

			# create medium image
			image.thumbnail((sizes['med']['w'], sizes['med']['h']), Image.ANTIALIAS)
			image.save(settings.UPLOAD_DISH + '/' + self.urlname+"-med."+ext.lower())

			# create thumbnail
			image.thumbnail((sizes['thum']['w'], sizes['thum']['h']), Image.ANTIALIAS)
			image.save(settings.UPLOAD_DISH + '/' + self.urlname+"-thum."+ext.lower())

		else:
			#file = self.location.url
			#if os.path.exists(file):
			#photopath = "https://wfgs.s3.amazonaws.com/media/{}".format(self.location.url)
			#print photopath
			print "self.location.url: "+str(self.location.url)
			import requests
			request = requests.get(self.location.url)
			if request.status_code == 200:
				## There is already a picture
				print "File exists: {}".format(self.location.url)
				import boto3
				#s3 = boto3.client('s3')
				s3 = boto3.resource('s3')
				bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
				loc = str(self.location.url)
				print "loc: "+loc
				#key = loc.split('/')[-1]
				#filename, extension = os.path.splitext(self.location.url)
				basename = os.path.basename(self.location.url)
				print "basename: {}".format(basename)
				filename, extension = os.path.splitext(basename)
				print "name1: {}, ext1: {}".format(name1, ext1)
				#key = str(basename)
				#print "bucket: {}, key: {}, path_tmp: {} ".format(bucket, key, path_tmp)
				print "self.urlname: {}, filename: {}, extension: {} ".format(self.urlname, filename, extension)
				#dirname = os.path.dirname(key)
				#oldkey = 'media/dishes/{}'.format(basename)
				oldkey = 'media/dishes/{}{}'.format(filename, extension)
				oldkey_reg = 'media/dishes/{}-reg{}'.format(filename, extension)
				oldkey_med = 'media/dishes/{}-med{}'.format(filename, extension)
				oldkey_thum = 'media/dishes/{}-thum{}'.format(filename, extension)
				print "oldkey: "+oldkey
				newkey = "media/dishes/{}{}".format(self.urlname,extension)
				print "newkey: "+newkey
				newkey_reg = "media/dishes/{}-reg{}".format(self.urlname,extension)
				newkey_med = "media/dishes/{}-med{}".format(self.urlname,extension)
				newkey_thum = "media/dishes/{}-thum{}".format(self.urlname,extension)
				#copy_source = {'Bucket': str(bucket), 'Key': key}
				s3.Object(bucket,newkey).copy_from(CopySource='wfgs/'+oldkey)
				s3.Object(bucket,newkey_reg).copy_from(CopySource='wfgs/'+oldkey_reg)
				s3.Object(bucket,newkey_med).copy_from(CopySource='wfgs/'+oldkey_med)
				s3.Object(bucket,newkey_thum).copy_from(CopySource='wfgs/'+oldkey_thum)
				#s3.Object(bucket,newname1).copy_from(CopySource=copy_source)
				#s3.Object('my_bucket','old_file_key').delete()
				#s3.download_file(Bucket=bucket, Key=key, Filename=path_tmp)
			else:
				print "File doesn't exists: {}".format(self.location.url)
			#super(Picture, self).save()
		UpdateMainPhoto(self.dish.pk)#Updates
		
	class Meta:
		ordering = ('dish__name',)

class LikePicture(models.Model):
	picture		= models.ForeignKey(Picture)
	profile		= models.ForeignKey(userProfile)
	likes = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s, %s"%(self.picture,self.profile)

class LikeDish(models.Model):
	dish		= models.ForeignKey(Dish)
	profile		= models.ForeignKey(userProfile)
	likes = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s, %s"%(self.dish,self.profile)
	class Meta:
		ordering = ('dish',)

class LikeList(models.Model):
	list		= models.ForeignKey(List)
	profile		= models.ForeignKey(userProfile)
	datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)
	#likes = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s, %s"%(self.list,self.profile)
	class Meta:
		ordering = ('list',)