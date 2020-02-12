# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage #To send emails
from django.db.models import Max
from inflection import singularize
from PIL import Image
import random
import operator
from operator import or_, and_ #For search advance
from django.core import serializers #For ajax consults
import string #to use string.capwords(myString) in Dish, List, Cuisine (names)
import json #for ajax in photonewnodish
from django.contrib.auth.decorators import login_required #For decorator: @login_required
from datetime import date, datetime #To calculate todays date
from django.contrib.auth.models import User
from dish import settings #To call media locations, MEDIA_URL, LOADING_IMG

#For login
from django.contrib.auth import login,logout,authenticate
import os #To delete photo
import unicodedata #For search. Converts: naïve café -> naive cafe
from django.contrib.sitemaps import Sitemap #For sitemaps
#from django.contrib.sitemaps.views import Sitemap
from django.core.urlresolvers import resolve, reverse, Resolver404#resolve(photonew),reverse(for Sitemap of static views)
from django.db.models import Q #dishlist_view, more
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount#For: 1)django-allauth in Myprofile, 2)Login
from allauth.account.models import EmailAddress #For: 1) unlink_account_view to delete email 2)signup_view to create email
from allauth.account.decorators import verified_email_required #to use descorator @verified_email_required from django-allauth
from dish.files.models import (
	Cuisine,
	EmailQueue,
	DishSimilar,
	Dish,
	Feature,
	LikePicture,
	LikeDish,
	List,
	ListDish,
	LikeList,
	Picture,
	SearchLog,
	userProfile,
	)
from dish.files.forms import (
	ContactForm,
	cuisine_Form,
	#Cuisine_Form,
	#dishnew_cf_Form,
	#dish_new_Form,
	dishForm,
	LoginForm,
	photoAdd_Form,
	photoEdit_Form,
	PassRecovForm,
	UpdatePasswordForm,
	UpdateEmailForm,
	UpdateUserForm,
	PrivacyForm,
	PicureProfileForm,
	SignupForm,
	UpdateAboutmeForm,
	#dish_edit_Form,
	photoRotate_Form,
	#photoAddNoDish_Form,
	search_Form,
	searchAdvance_Form,
	photoCrop_Form,
	similar_Form,
	#list_new_Form,
	List_Form,
	search_list_Form,
	dishphotoForm,
	list_dish_comment_Form,
)


singin_url = '/signin/'
		
def authorized_digital_sellers_view(request):
	"""Generates ads.txt required by google adSense"""
	return HttpResponse('google.com, pub-3566007766704147, DIRECT, f08c47fec0942fa0')

class StaticViewSitemap(Sitemap):
	changefreq = 'daily'
	priority = 1.0
	lastmod = datetime.now()
	def items(self):
		return [
			'view_main',
			'view_login',
			'view_signup',
			'view_about',
			'view_contact',
			'view_help',
			'view_guidelines',
			'view_terms',
			'view_passrecovery',
			'view_myprofile',
			'view_privacy',
			'view_cuisinenew',
			'view_latestphotos',
			'view_searchadvance',
		]

	def location(self, item):
		return reverse(item)

class CuisinesSitemap(Sitemap):
	changefreq = 'daily'
	priority = 0.9
	lastmod = datetime.now()
	def items(self):
		return Cuisine.objects.filter(active=True)

class DishesSitemap(Sitemap):
	changefreq = 'daily'
	priority = 0.8
	lastmod = datetime.now()
	def items(self):
		return Dish.objects.filter(active=True)

class PicturesSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 0.7
	lastmod = datetime.now()
	def items(self):
		return Picture.objects.filter(active=True)

class ListSitemap(Sitemap):
	changefreq = 'daily'
	priority = 0.6
	lastmod = datetime.now()
	def items(self):
		return List.objects.filter(active=True,private=False)

class MembersSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 0.5
	lastmod = datetime.now()
	def items(self):
		return userProfile.objects.all()

def SaveEmailQueue(username,obj,action,url=None):
	send = EmailQueue()
	send.date = datetime.now()
	send.username = username
	send.object = obj
	send.action = action
	if url:
		send.url_plus = url
	send.sent_flag = False
	send.save()
	#from dish.files.extra.cron_jobs import CheckEmails
	#CheckEmails()

def UpdateMainPhoto(id_dish):
	print "Updatting main_photo in views"
	dish = Dish.objects.get(pk=id_dish)
	favphoto = Picture.objects.filter(dish=dish.id).order_by('-likestot','-datetime').first()
	print "favphoto:"
	print favphoto
	if favphoto:
		## There is a photo, use obj
		print "There is a photo, use obj"
		dish.photo_main = str(favphoto.location)
		print str(favphoto.location)
	else:
		## There is no photo, clear photo_m
		print "There is no photo, clear photo_m"
		dish.photo_main = ""
	dish.save()

def index_view(request):
	cuisine_top = Cuisine.objects.all().annotate(Count('dish', distinct = True)).annotate(Count('dish__picture')).order_by('-dish__picture__count')[:6]
	foofies_top = userProfile.objects.annotate(Count('picture')).annotate(Count('list')).select_related('user').distinct().order_by('-picture__count')[:5]
	dishes_latest = Dish.objects.filter(active=True).prefetch_related('cuisines').order_by('-datetime')[:6]
	lists = List.objects.filter(active=True).exclude(type = '3').select_related('owner__user').prefetch_related('dishes').order_by('-likestot')[:5]
	cxt = {'cuisine_top':cuisine_top, 'foofies_top':foofies_top, 'dishes_latest':dishes_latest,'top_lists':lists}
	return render_to_response('_main.html',cxt,context_instance=RequestContext(request))

#################################
######  C U I S I N E S   #######
#################################
def cuisines_view(request,page=None):
	list = Cuisine.objects.filter(active=True).order_by('name')
	#list = Cuisine.objects.filter(active=True).select_related(Prefetch('photo',queryset = Picture.objects.filter(dish__cuisines=self.id).order_by('-likestot').first())
	
	paginator = Paginator(list,20) # 10 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist}
	return render_to_response('cuisines.html',cxt,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def cuisinenew_view(request):
	info = 0
	cuisines = Cuisine.objects.filter(active=1).order_by('name')
	if request.method == "POST":
		form = cuisine_Form(request.POST)
		if form.is_valid():
			nami = form.cleaned_data['name']
			nami = nami.replace('Cuisine', '').replace('cuisine', '').strip()
			nami = nami.title()
			"""
			if nami[0] == '-':
				nami=string.capwords(nami[1:])
				nami="-"+nami
			else:
				nami=string.capwords(nami)
			"""
			#nami = string.capwords(nami)
			check = form.cleaned_data['check']
			othernames = form.cleaned_data['othernames'].strip().title()
			territory = form.cleaned_data['territory'].strip().title()
			description = form.cleaned_data['description']
			cui = Cuisine.objects.filter(name=nami)
			if cui.exists():
				cu = cui.get(name=nami)
				info = 1
				form = cuisine_Form(initial={'name':nami,'othernames':othernames,'territory':territory,'description':description,'check':0})
				ctx = {'form':form, 'information':info, 'cuisine':cui, 'rep':cu, 'check':0}
				return render_to_response('cuisinenew.html',ctx,context_instance=RequestContext(request))
			if check == 1:
				#print 'checking:'+str(check)
				if len(othernames)>1:
					othernames = string.capwords(othernames)
					othernames_list = othernames.split(',')
					sim_cui = cuisines.filter(reduce(or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in othernames_list]))
					if sim_cui:
						#There are similarities with other names
						info = 4
						form = cuisine_Form(initial={'name':nami,'othernames':othernames,'territory':territory,'description':description,'check':0})
						ctx = {'form':form, 'information':info, 'similars':sim_cui, 'check':0}
						return render_to_response('cuisinenew.html',ctx,context_instance=RequestContext(request))
			#print 'Not checking:'+str(check)
			p = Cuisine()
			p.name = nami
			p.othernames = othernames
			p.territory = territory
			p.description = description
			p.active = True
			urlname =  nami.lower().replace(" ", "_")
			urlname =  urlname.replace("'", "")
			p.urlname =  urlname
			req_user = request.user
			profile = userProfile.objects.get(user=req_user)
			p.owner = profile
			p.save() # Guardar la informacion
			#email_url='http://worldfood.guide/cuisine/%s/'%(urlname)
			email_url = request.build_absolute_uri('/')+'cuisine/%s/'%(urlname)
			SaveEmailQueue(request.user.username,'Cuisine','Added',email_url)
			info = 2
			return HttpResponseRedirect('/cuisine/%s/'%(urlname))
		else:
			info = 3
			ctx = {'form':form, 'check':0}
			return render_to_response('cuisinenew.html',ctx,context_instance=RequestContext(request))
	form= cuisine_Form()
	ctx = {'form':form, 'information':info, 'cuisine':cuisines, 'check':1}
	return render_to_response('cuisinenew.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def cuisineedit_view(request, id):
	info = 0
	cuisine = Cuisine.objects.get(pk=id)
	cuisines = Cuisine.objects.filter(active=1).order_by('name')
	if request.method == "POST":
		form = cuisine_Form(request.POST)
		if form.is_valid():
			nami = form.cleaned_data['name'].replace('Cuisine', '').replace('cuisine', '').strip()
			nami = nami.title()
			check = form.cleaned_data['check']
			description = form.cleaned_data['description']
			othernames = form.cleaned_data['othernames'].strip().title()
			territory = form.cleaned_data['territory'].strip().title()
			cui = Cuisine.objects.filter(name=nami).exclude(pk=id)
			if cui.exists():
				cu = cui.get(name=nami)
				info = 1
				form = cuisine_Form(initial={'name':nami,'othernames':othernames,'description':description,'check':0})
				ctx = {'form':form, 'information':info, 'cuisine':cuisine, 'rep':cu, 'check':0}
				return render_to_response('cuisineedit.html',ctx,context_instance=RequestContext(request))
			if check == 1:
				#print 'checking:'+str(check)
				if len(othernames)>1:
					othernames = string.capwords(othernames)
					othernames_list = othernames.split(',')
					#print "othernames in list:"+str(len(othernames_list))
					#print othernames_list
					sim_cui = cuisines.filter(reduce(or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in othernames_list])).exclude(pk=id)
					if sim_cui:
						#There are similarities with other names
						info = 4
						form = cuisine_Form(initial={'name':nami,'othernames':othernames,'description':description,'check':0})
						ctx = {'form':form, 'cuisine':cuisine, 'information':info, 'similars':sim_cui, 'check':0}
						return render_to_response('cuisineedit.html',ctx,context_instance=RequestContext(request))
			#print 'Not checking:'+str(check)
			cuisine.name = nami
			cuisine.othernames = othernames
			cuisine.territory = territory
			cuisine.description = description
			urlname =  nami.lower().replace(" ", "_")
			urlname =  urlname.replace("'", "")
			cuisine.urlname =  urlname
			cuisine.save() # Guardar la informacion
			info = 2
			return HttpResponseRedirect('/cuisine/%s/'%(urlname))
		else:
			info = 3
			ctx = {'form':form, 'check':0}
			return render_to_response('cuisineedit.html',ctx,context_instance=RequestContext(request))
	form = cuisine_Form(initial={'name':cuisine.name,'othernames':cuisine.othernames,'territory':cuisine.territory,'description':cuisine.description,'check':0})
	ctx = {'form':form, 'information':info, 'cuisine':cuisine,'check':0}
	return render_to_response('cuisineedit.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def cuisinedelete_view(request, urlname):
	info = 0
	cuisine = Cuisine.objects.get(urlname=urlname)
	dishes = Dish.objects.filter(cuisines=cuisine)
	if request.method == "POST":
		if len(dishes)>0:
			info = 1
		else:
			cuisine.delete()
			req_user = request.user
			SaveEmailQueue(request.user.username,'Cuisine','Deleted',cuisine.urlname)
			return HttpResponseRedirect('/cuisines/1/')
	if len(dishes)>0:
		info = 1
	ctx = {'information':info, 'cuisine':cuisine, 'dishes':dishes}
	return render_to_response('cuisine_delete.html',ctx,context_instance=RequestContext(request))
	
def cuisine_redirect_view(request,id):
	cui = Cuisine.objects.get(pk=id)
	return cuisine_view(request,cui.urlname)

def cuisine_view(request,urlname):
	cui = Cuisine.objects.get(urlname=urlname)
	dishes_total = Dish.objects.filter(active=True, cuisines=cui.id).count()
	liked_dishes = Dish.objects.filter(active=True, cuisines=cui.id).prefetch_related('cuisines').order_by('-likestot')[:7]
	dishes_count = liked_dishes.count()
	ctx = {'cuisine':cui,'liked_dishes':liked_dishes,'dishes_total':dishes_total,'dishes_count':dishes_count}
	return render_to_response('cuisine.html',ctx,context_instance=RequestContext(request))

def cuisinedishes_redirect_view(request,id_cuis,page):
	cui = Cuisine.objects.get(pk=id_cuis)
	return cuisinedishes_view(request,cui.urlname,page)

def cuisinedishes_view(request,urlname,page=None):
	cui = Cuisine.objects.get(urlname=urlname)
	#list = Dish.objects.filter(active=True,cuisines=cui.id).prefetch_related('cuisines').order_by('name')
	list = Dish.objects.filter(active=True,cuisines=cui.id).select_related('userprofile').prefetch_related('cuisines').annotate(Count('picture')).order_by('name')
	#fav_pic = Dish.objects.filter(cuisines=cui,picture__likepicture__likes=1).annotate(num_likes=Count('picture__likepicture__likes')).order_by('-num_likes')
	fav_pic = Dish.objects.filter(cuisines=cui).annotate(count=Count('picture__likepicture')).order_by('-count')[:1]
	if fav_pic:
		fav_pic = fav_pic[0]
	else:
		fav_pic= None
	paginator = Paginator(list,20) # 10 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'obj':cui,'fav_pic':fav_pic,'paginatorlist':paginatorlist}
	return render_to_response('cuisinedishes.html',cxt,context_instance=RequestContext(request))

def cuisines_result_view(request,search=None,page=None):
	all_cuisines = Cuisine.objects.all()
	all_cuisines = all_cuisines.filter(Q(name__icontains=search) | Q(othernames__icontains=search))
	paginator = Paginator(all_cuisines,10)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist, 'search':search}
	return render_to_response('cuisines_result.html',cxt,context_instance=RequestContext(request))

def cuisine_search(string_sent):
	#print "---------------------in search cuisine--------------"
	string_stripped = ' '.join(string_sent.split())#Removes any multiple spaces
	#print str(string_stripped)
	counter = 0
	results = Cuisine.objects.none()
	if string_stripped:#If string is not empty
		#print "Si hay string_stripped"
		## Searches exact string, spaces cleared
		all_rows = Cuisine.objects.filter(active=True)
		results = all_rows.filter(Q(name__iexact=string_stripped) | Q(othernames__iexact=string_stripped))
		counter = len(results)
		#print "Search with iexact in name and othernames: "+str(counter)
		if counter < 1:
		#search commpleate frace in othernames with commas
			#print "No results with iexact in name and othernames. Will search icontains in othernames"
			list_with_commas = []
			list_with_commas.append(", "+string_stripped)
			list_with_commas.append(","+string_stripped)
			list_with_commas.append(string_stripped+",")
			list_with_commas.append(string_stripped+" ,")
			#results = all_rows.filter((othernames__icontains=c) for c in list_with_commas)
			results = all_rows.filter(reduce(operator.or_, [Q(othernames__iexact=c) for c in list_with_commas]))
			counter = len(results)
			#print "Searching: "
			#print list_with_commas
			#print "with iexact in othernames using or, resulst: "+str(counter)
			if counter < 1:
				#Search commplete frace in names and othernames with no S at the end of words
				#print "no results for -"+str(string_stripped)+"-, in first stage: Exact frace, spaces cleared. Now clearing S"
				string_no_s = ' '.join([item.rstrip('s') for item in string_stripped.split()])
				#Searches exact string, S cleared
				results = all_rows.filter(Q(name__iexact=string_no_s) | Q(othernames__iexact=string_no_s))
				counter = len(results)
				#print "Results with iexact in name and othernames with S cleared: "+str(counter)
				if counter < 1:
					#Search combination of words with spaces in name and othernames
					#clears words with less than 3 letters, so it doesn't look for 'of' 'a', etc
					#print "no results for -"+str(string_no_s)+"-, in second stage: Exact frace, S cleared, now combine words"
					search_list = string_no_s.split()
					#Python3: change xrange for range
					AVOID_3 = ('con','del',)
					for i in xrange(len(search_list) - 1, -1, -1):#While iterate going backwards so index continue when removing element
						if len(search_list[i]) < 3 or search_list[i].lower() in AVOID_3:
							del search_list[i]
					#print "Will search iexact in name and othernames from list:"
					#print search_list
					results = all_rows.filter(reduce(operator.and_, [Q(name__iexact=c)|Q(othernames__iexact=c) for c in search_list]))
					counter = len(results)
					#print "Results with combined words using and_, iexact: "+str(counter)
					#print results
					if counter < 1:
						#print "Will search for: "
						#print search_list
						results = all_rows.filter(reduce(operator.or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in search_list]))
						counter = len(results)
						#print "Results with combined words using icontains: "+str(counter)					
						if counter < 1:
							#Adding spaces to words 
							#search_list = [" "+word for word in search_list]
							list_blank_left = [" "+word for word in search_list]
							list_blank_right = [word+" " for word in search_list]
							list_with_blanks = list_blank_left + list_blank_right
							#print "Searching icontains for names and othernames from list with blanks:"
							#print list_with_blanks
							#Searcheed one word
							results = all_rows.filter(reduce(operator.or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in list_with_blanks]))
							counter = len(results)
							#print "Results with combined words: "+str(counter)
	return results
	
#################################
######   D I S H          #######
#################################

def dishes_view(request,page=None):
	from django.db.models.functions import Substr
	list = Dish.objects.filter(active=True).select_related('userprofile__user').prefetch_related('cuisines').annotate(Count('picture'))
	#list = Dish.objects.filter(active=True).select_related('userprofile').prefetch_related('cuisines','dishpicture')
	paginator = Paginator(list,20) # 10 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist}
	return render_to_response('dishes.html',cxt,context_instance=RequestContext(request))

def disheslatest_view(request,page=None):
	#list = Dish.objects.filter(active=True).prefetch_related('cuisines').annotate(Count('picture')).order_by('-datetime')
	list = Dish.objects.filter(active=True).prefetch_related('cuisines').order_by('-datetime')
	paginator = Paginator(list,20) # 20 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist}
	return render_to_response('disheslatest.html',cxt,context_instance=RequestContext(request))
	
def dishredirect_view(request,id):
	dish = Dish.objects.get(pk=id)
	#ctx = Context({'patherror':request.path})
	#return HttpResponse(content=template.render(ctx), content_type='text/html; charset=utf-8', status=301)
	return dish_view(request,dish.urlname)
	
def dish_view(request,urlname):
	req_user = request.user
	try:
		dish = Dish.objects.prefetch_related('cuisines','userprofile__user').get(urlname=urlname)
	except Dish.DoesNotExist:
		#In case the url doesn't exist. Don't send a error page since the page have might be deleted, send it to a search to find a similar dish
		names_list = urlname.split('_')
		list_len = len(names_list)
		#print "list_len: "+str(list_len)
		if list_len > 1:
			#print "list_len > 1:"
			if names_list[list_len-1].isdigit():
				#print names_list[list_len-1]+ " is a digit"
				search_for = "+".join(names_list[0:list_len-1])
			else:
				#print "no digit"
				search_for = "+".join(names_list)
		else:
			search_for = "+".join(names_list)
		return HttpResponseRedirect('/searchresultadv/%s/*/*/1/'%(search_for))
	desc=dish.description
	desc_small = desc[:500]
	desc_mobile = desc[:200]
	#from django.db.models import Max
	photos = Picture.objects.filter(dish=dish.id).select_related('owner__user').order_by('-likestot','-datetime')[:5]
	liked = 0
	#lists = List.objects.filter(dishes=dish,active=True).select_related('owner').order_by('-likestot')
	lists = List.objects.filter(dishes=dish,active=True).prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner').order_by('-likestot')
	list_total = lists.count()
	similars = DishSimilar.objects.filter(dish1=dish).select_related('dish2').prefetch_related('dish2__cuisines')
	similar_total = similars.count()
	ctx = {'dish':dish,'photos':photos,'similars':similars, 'desc_small':desc_small,'desc_mobile':desc_mobile, 'liked':liked, 'lists':lists, 'list_total':list_total,'similar_total':similar_total}
	if req_user.is_authenticated():
		req_profile = userProfile.objects.get(user=req_user)
		lists = lists.exclude(~Q(owner = req_profile), type = '3')
		list_count = lists.count()
		try:
			obj = LikeDish.objects.get(profile=req_profile, dish=dish)
			if obj.likes == 1:
				liked = 1
		except:
			liked = 0
		ctx.update({'liked':liked, 'lists':lists, 'list_count':list_count})
	else:
		lists = lists.exclude(type = '3')
		list_count = lists.count()
		## Adds info to ctx dic
		ctx.update({'lists':lists, 'list_count':list_count})
	return render_to_response('dish.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def dishedit_view(request,id):
	f = Dish.objects.get(id=id)
	#print f.features.all
	urlname = f.urlname
	old_urlname = urlname
	cui_query = Cuisine.objects.filter(dish__id=f.id)
	current_query_features = Feature.objects.filter(dish__id=f.id)
	feature_current_id_list = Feature.objects.filter(dish__id=f.id).values_list('id', flat=True)
	query_features = Feature.objects.all()
	if request.method == "POST":
		form = dishForm(request.POST)
		## 2 Form Valid ? ###
		if form.is_valid():
			## 3 Get Form data ###
			name_f = form.cleaned_data['name'].strip().title()
			name_f = name_f.replace("'S", "'s")
			othernames = form.cleaned_data['othernames'].strip()
			ingredients = form.cleaned_data['ingredients'].strip()
			desc = form.cleaned_data['description']
			cuisine_list = request.POST.getlist('cuisines')
			features_list = request.POST.getlist('feature')
			new_query_features = Feature.objects.filter(name__in=features_list)
			#print features_list
			cui_query_n = Cuisine.objects.filter(pk__in=cuisine_list)
			dishes = Dish.objects.filter(active=1).exclude(id=f.id).order_by('name')#all active dishes, except edditing dish
			othernames_list = [x.strip() for x in othernames.split(',')]
			othernames_list = filter(None, othernames_list)
			if len(othernames_list)>0:#There are othernames, used them
				duplicate = dishes.filter(Q(name__iexact=name_f) | Q(othernames__iexact=name_f) | reduce(or_, [Q(name__iexact=c)|Q(othernames__iexact=c) for c in othernames_list]), cuisines__in=cuisine_list).distinct()
			else:
				duplicate = dishes.filter(Q(name__iexact=name_f) | Q(othernames__iexact=name_f) , cuisines__in=cuisine_list).distinct()
			## 5 - Exact duplaicated ? ###
			if duplicate.exists():
				#Duplicated exist, send info back with alert
				form = dishForm(initial={'name':name_f,'othernames':othernames,'ingredients':ingredients,'description':desc})
				ctx = {'form':form,'dish':f, 'list':duplicate,'cuisines':cui_query_n, 'features':query_features, 'features_selected':current_query_features, 'feature_current_id_list':feature_current_id_list}
				return render_to_response('dishedit.html',ctx,context_instance=RequestContext(request))
			### 7 - Name different than original name? ###
			if name_f != f.name:
				### 8 - Generate urlname ###
				urlname =  name_f.lower().replace (" ", "_").replace("'", "").replace(".", "")
				if (Dish.objects.filter(urlname=urlname).exclude(id=f.id).count()==0):
					urlname = urlname
				else:
					x = 1
					tempname = urlname
					while (Dish.objects.filter(urlname=tempname+"_"+str(x)).count() > 0):
						x=x+1
					urlname = tempname+"_"+str(x)
			### 9 - Save Dish ###
			req_user = request.user
			f.name = name_f
			f.urlname = urlname
			f.description = desc
			f.othernames = othernames
			f.ingredients = ingredients
			f.userprofile = userProfile.objects.get(user=req_user)
			f.datetime = datetime.now()
			f.save()
			#f.features.add(feat_query_n)
			### 10 - Cuisines Changed? ###
			if cui_query != cui_query_n:
				### 11 - Save Cuisines
				for cui_o in cui_query:
					f.cuisines.remove(cui_o.id)#.delete()
				for cui in cui_query_n:
					f.cuisines.add(cui.id)
			### Features Changed? ###
			if current_query_features != new_query_features:
				for feat in current_query_features:
					f.features.remove(feat.id)#.delete()
				for feat in new_query_features:
					f.features.add(feat.id)
			### 12 - Are there pictures? ###
			pictures = Picture.objects.filter(dish__id=f.id)
			if pictures:
				for pic in pictures:
					pic.urlname = str(f.urlname)+'_'+str(pic.id)
					pic.save()
				## Update photo_main:
				UpdateMainPhoto(f.pk)
			###  14 - redirect to dish ##
			return HttpResponseRedirect('/dish/%s/'%(f.urlname))
		else:
			#print "Form not valid"
			### 12 - Form not valid, Return ###
			ctx = {'form':form,'dish':f,'cuisines':cui_query,'cuisines_h':cui_query}
			return render_to_response('dishedit.html',ctx,context_instance=RequestContext(request))
	### 13 - Populate form ###:
	form=dishForm(initial={'name':f.name,'othernames':f.othernames,'ingredients':f.ingredients,'description':f.description, 'features':f.features.all})
	ctx = {'form':form,'dish':f,'cuisines':cui_query, 'cuisines_h':cui_query, 'features':query_features, 'features_selected':current_query_features, 'feature_current_id_list':feature_current_id_list,'MEDIA_URL':settings.MEDIA_URL}
	return render_to_response('dishedit.html',ctx,context_instance=RequestContext(request))
#111
@login_required(login_url=singin_url)
@verified_email_required
def dishphotonew_view(request,id_cui=None,name=None):
	#id_cui = Cuisine pk, When a cuisine is sent
	if id_cui==None or id_cui==0:
		cui = {}
	else:
		cui = Cuisine.objects.filter(pk=id_cui)
	query_features = Feature.objects.all()
	if request.method == "POST":
		form = dishphotoForm(request.POST, request.FILES)
		## Form Valid ? ###
		if form.is_valid():
			## Get Form data ###
			dish_selected = form.cleaned_data['dish']
			photo = form.cleaned_data['location']
			ownit = form.cleaned_data['ownit']
			creditsname = form.cleaned_data['creditsname'].strip()
			creditsurl = form.cleaned_data['creditsurl']
			comm = form.cleaned_data['comments']
			#print type(dish_selected)
			if dish_selected == 0:
				#new dish
				name_f = string.capwords(form.cleaned_data['name'].strip())
				othernames = string.capwords(form.cleaned_data['othernames'].strip())
				ingredients = form.cleaned_data['ingredients'].strip()
				desc = form.cleaned_data['description']
				cuisine_list = request.POST.getlist('cuisines')
				features_list = request.POST.getlist('feature')
				cui_query_n = Cuisine.objects.filter(pk__in=cuisine_list)#for form initial
				new_query_features = Feature.objects.filter(name__in=features_list)
				dishes = Dish.objects.filter(active=1).order_by('name')#all active dishes
				othernames_list = [x.strip() for x in othernames.split(',')]
				othernames_list = filter(None, othernames_list)
				if len(othernames_list)>0:#There are othernames, used them
					duplicate = dishes.filter(Q(name__iexact=name_f) | Q(othernames__iexact=name_f) | reduce(or_, [Q(name__iexact=c)|Q(othernames__iexact=c) for c in othernames_list]), cuisines__in=cuisine_list).distinct()
				else:
					duplicate = dishes.filter(Q(name__iexact=name_f) | Q(othernames__iexact=name_f) , cuisines__in=cuisine_list).distinct()
				## 5 - Exact duplaicated ? ###
				if duplicate.exists():
					#Duplicated exist, send info back with alert
					form = dishphotoForm(initial={'name':name_f,'othernames':othernames,'ingredients':ingredients,'description':desc})
					ctx = {'form':form, 'list':duplicate,'cuisines':cui_query_n,'location':photo,'comments':comm, 'features':query_features}
					return render_to_response('dishnew.html',ctx,context_instance=RequestContext(request))
				#No changes or populating form for first time
				urlname =  name_f.lower().replace(" ", "_").replace("'", "").replace(".", "")
				if (Dish.objects.filter(urlname=urlname).count()==0):
					#there are no similar urls in system
					urlname = urlname
				else:
					#There is/are similar urls in the system, add 1 and keep checking for similarities
					x = 1
					tempname = urlname
					while (Dish.objects.filter(urlname=tempname+"_"+str(x)).count() > 0):
						x=x+1
					urlname = tempname+"_"+str(x)
				###Create and save new Dish() ###
				req_user = request.user
				d = Dish()
				d.name = string.capwords(name_f)
				d.urlname = urlname
				d.othernames = othernames
				d.ingredients = ingredients
				d.description = desc
				d.userprofile = userProfile.objects.get(user=req_user)
				d.datetime = timezone.now()
				d.likestot = 0
				d.active = 1
				d.save()
				for cui in cui_query_n:
					d.cuisines.add(cui.id)
				### Features  ###
				for feat in new_query_features:
					d.features.add(feat.id)
				email_url=request.build_absolute_uri('/')+'dish/%s/'%(d.urlname)
				SaveEmailQueue(req_user.username,'Dish','Added',email_url)
				## Check if user uploaded a photo
				if photo:
					## New photo uploading
					p = Picture()
					#Save new photo
					p.location = photo
					p.ownit = ownit
					p.creditsname = creditsname
					p.creditsurl = creditsurl
					p.comments = comm
					getKey = Picture.objects.aggregate(next=Max('id'))['next']
					p.urlname = str(d.urlname)+'_'+str(getKey+1)
					p.datetime = timezone.now()
					p.active = 1
					p.dish = d
					p.likestot = 0
					profile = userProfile.objects.get(user=req_user)
					p.owner = profile
					p.save()
					email_url=request.build_absolute_uri('/')+'photo/%s/'%(p.urlname)
					SaveEmailQueue(req_user.username,'Photo','Added',email_url)
					if not settings.LOCAL_DEV:
						##Change location from dishes_original to dishes
						loc = str(p.location)
						p.location = loc.replace("dishes_original/", "dishes/")
						p.save()
						## code that waits until S3 finished creating thumbnails with lambda (only production)
						#photopath = "https://wfgs.s3.amazonaws.com/media/{}".format(p.location)
						photopath = settings.MEDIA_URL+str(p.location)
						print "photopath: {}".format(photopath)
						import requests
						import time
						for x in range(20):
							## If the request of the photo is 200, it exists and redirects to photo
							print "Second in try: "+str(x)
							request = requests.get(photopath)
							if request.status_code == 200:
								print "resoleved, redirecting to /photo/"
								return HttpResponseRedirect('/dish/%s/'%(d.urlname))
							else:
								## If request is not 200, lambda is still working, waits 1 second and ask again
								x=+1
								time.sleep(1)
						return HttpResponseRedirect('/dish/%s/'%(d.urlname))
					else:
						## If we are in development, it doesn't need to wait for lambda
						return HttpResponseRedirect('/dish/%s/'%(d.urlname))
				return HttpResponseRedirect('/dish/%s/'%(d.urlname))
			else:#No new dish was created, the user selected one from the system. Check for photo
				if photo:
					dish = Dish.objects.get(id=dish_selected)
					p = Picture()
					p.location = photo
					p.ownit = ownit
					p.creditsname = creditsname
					p.creditsurl = creditsurl
					p.comments = comm
					getKey = Picture.objects.aggregate(next=Max('id'))['next']
					p.urlname = str(dish.urlname)+'_'+str(getKey+1)
					#p.likes = 0
					p.datetime = datetime.now()
					p.active = 1
					p.dish = dish
					p.likestot = 0
					req_user = request.user
					profile = userProfile.objects.get(user=req_user)
					p.owner = profile
					p.save() # Guardar la informacion
					email_url=request.build_absolute_uri('/')+'photo/%s/'%(p.urlname)
					SaveEmailQueue(req_user.username,'Photo','Added',email_url)
					if not settings.LOCAL_DEV:
						##Change location from dishes_original to dishes
						loc = str(p.location)
						p.location = loc.replace("dishes_original/", "dishes/")
						p.save()
						## code that waits until S3 finished creating thumbnails with lambda (only production)
						#photopath = "https://wfgs.s3.amazonaws.com/media/{}".format(p.location)
						photopath = settings.MEDIA_URL+str(p.location)
						#print "photopath: {}".format(photopath)
						import requests
						import time
						for x in range(20):
							## If the request of the photo is 200, it exists and redirects to photo
							#print "Second in try: "+str(x)
							request = requests.get(photopath)
							if request.status_code == 200:
								#print "resoleved, redirecting to /photo/"
								return HttpResponseRedirect('/dish/%s/'%(d.urlname))
							else:
								## If request is not 200, lambda is still working, waits 1 second and ask again
								x=+1
								time.sleep(1)
						return HttpResponseRedirect('/dish/%s/'%(d.urlname))
					else:
						## If we are in development, it doesn't need to wait for lambda
						return HttpResponseRedirect('/dish/%s/'%(d.urlname))
		else:
			### Form not valid, Return ###
			#print "Form not valid: "+str(form.errors.as_text)
			ctx = {'form':form, 'features':query_features}
			return render_to_response('dishnew.html',ctx,context_instance=RequestContext(request))
	### 13 - Render form ###
	#print "initial name: "+str(name)
	form = dishphotoForm(initial={'cuisines':cui,'name':name,'name_h':name})
	ctx = {'form':form, 'cuisines':cui, 'features':query_features}
	return render_to_response('dishnew.html',ctx,context_instance=RequestContext(request))

#Templeate: dish, Modal that adds dish to list
@login_required(login_url=singin_url)
def dish_addto_simimar_view(request,dish_id,similar_id):
	user_logged = request.user
	similar = Dish.objects.get(pk= similar_id)
	dish = Dish.objects.get(pk= dish_id)
	owner = userProfile.objects.get(user=user_logged)
	obj, created = DishSimilar.objects.get_or_create(dish1=dish, dish2=similar, profile=owner, datetime=datetime.now())
	obj, created = DishSimilar.objects.get_or_create(dish1=similar, dish2=dish, profile=owner, datetime=datetime.now())
	return redirect('view_dish', urlname = dish.urlname)

#Templeate: dish, Modal that adds dish to list
@login_required(login_url=singin_url)
def dish_addto_list_view(request,dish_id,list_id,url_return):
	user_logged = request.user
	list = List.objects.get(pk= list_id)
	dish = Dish.objects.get(pk= dish_id)
	# 1 = Personal:Publicaly available.Only I can add edit
	# 2 = Public: Anybody can edit
	# 3 = Private: Only I can see it
	if  list.type == '2' or (list.type != '2' and user_logged == list.owner.user):
		# list public or sent by owner, proceed to add dish to list
		dishes_total = ListDish.objects.filter(list=list).count()
		listdish = ListDish()
		listdish.list = list
		listdish.dish = dish
		listdish.index = dishes_total+1
		listdish.owner = userProfile.objects.get(user=user_logged)
		listdish.save()
	#print "url_return: "+str(url_return)
	if url_return == 'dish':
		return redirect('view_dish', urlname = dish.urlname)
	
def dishes_result_view(request,search=None,page=None):
	#all_dishes = Dish.objects.all()
	all_dishes = Dish.objects.filter(active=True).select_related('userprofile').prefetch_related('cuisines').annotate(Count('picture'))
	all_dishes = all_dishes.filter(Q(name__icontains=search) | Q(othernames__icontains=search))
	paginator = Paginator(all_dishes,10)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist, 'search':search,'all_dishes':all_dishes,}
	return render_to_response('dishes_result.html',cxt,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def dishdelete_view(request, id):
	info = 0
	dish = Dish.objects.get(pk=id)
	pictures = Picture.objects.filter(dish=dish)
	if request.method == "POST":
		if len(pictures)>0:
			info = 1
		else:
			req_user = request.user
			#profile = userProfile.objects.get(user=req_user)
			SaveEmailQueue(req_user.username,'Dish','Deleted',dish.urlname)
			dish.delete()
			return HttpResponseRedirect('/dishes/1/')
	if len(pictures)>0:
		info = 1
	ctx = {'information':info, 'dish':dish, 'pictures':pictures}
	return render_to_response('dishdelete.html',ctx,context_instance=RequestContext(request))

#############################
######    L I S T     #######
#############################

def list_view(request,urlname):
	alert = ""
	cxt = {}
	list = List.objects.select_related('owner__user').get(urlname=urlname)
	if list:
		# Ask if list is not private or (list is private AND user autenticated AND user is owner)
		if list.type != '3' or (list.type == '3' and request.user.is_authenticated() and list.owner.user == request.user):
			# List not private, or user authenticated and owner of list
			dishes= ListDish.objects.filter(list=list).select_related('list','dish','owner__user').prefetch_related('dish__cuisines').order_by('index')
			counter= dishes.count()
			desc=list.description
			desc_small = desc[:500]
			desc_mobile = desc[:200]
			#print "there is list:"+str(dishes)
			req_user = userProfile()
			alert = 1
			liked = 0
			if request.user.is_authenticated():
				req_user = userProfile.objects.get(pk=request.user.pk)
				try:
					obj = LikeList.objects.get(profile=req_user, list=list)
					if obj:
						liked = 1
				except:
					liked = 0
			cxt = {'list':list,'counter':counter,'alert':alert,'dishes':dishes,'user_req':req_user,'liked':liked,'desc_small':desc_small,'desc':desc,'desc_mobile':desc_mobile}
			# 1 = Personal:Publicaly available.Only I can add edit
			# 2 = Public: Anybody can edit
			# 3 = Private: Only I can see it
			return render_to_response('list.html',cxt,context_instance=RequestContext(request))
		else:
			# list,type != 3, that means it is public or personal, people can see it
			return redirect('view_lists', page='1', alert = list.type)

def list_search_view(request,search=None,alert=None,):
	if request.method == "POST":
		form = search_list_Form(request.POST or None)
		if form.is_valid():
			search_text = form.cleaned_data['search']
			#print 'Form valid, search sent by form: '+search_text
			return list_search_results_view(request,search_text,1)
	form = search_list_Form()
	cxt = {'form':form,'alert':alert,'search':search}
	return render_to_response('list_search.html',cxt,context_instance=RequestContext(request))

def quick_search_list_view(request):
#Comes from quick search form in lists results
	if request.method == "POST":
		form = search_Form(request.POST or None)
		if form.is_valid():
			search = form.cleaned_data['search']
			source = form.cleaned_data['source']
			search = search.strip()#Removes beginning and ending blanks
			search = unicodedata.normalize('NFKD', search).encode('ASCII', 'ignore')#converts: naïve café -> naive cafe
			req_user = request.user
			#Store seach words in SearchLog if not me
			if req_user.is_authenticated():
				if req_user.username != 'itisclaudio':
					new_search = SearchLog()
					profile = userProfile.objects.get(user=req_user)
					new_search.foodie = profile
					new_search.datetime = datetime.now()
					new_search.search_origin = source
					new_search.searchwords = search
					new_search.save()
			else:
				new_search = SearchLog()
				new_search.datetime = datetime.now()
				new_search.search_origin = source
				new_search.searchwords = search
				new_search.save()
			return list_search_results_view(request,search,1)
	#return redirect('searchadvance_view')
	return list_search_view(request)

#222
def list_search(string_sent):
	#print "---------in list_search---------"
	string_stripped = ' '.join(string_sent.split())#Removes any multiple spaces
	#print str(string_stripped)
	counter = 0
	results = List.objects.none()
	if string_stripped:#If string is not empty
		all_rows = List.objects.filter(active=True).prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner__user')
		results = all_rows.filter(name__iexact=string_stripped)
		counter = len(results)
		#print "Result for "+string_stripped+" in First search original name with iexact: "+str(counter)
		if counter < 1:
			#string_stripped_before = string_stripped.split()
			search_list_no_s = [item.rstrip('s') for item in string_stripped.split()]
			string_no_s = " ".join(str(x) for x in search_list_no_s)
			results = all_rows.filter(name__iexact=string_no_s)
			counter = len(results)
			#print "Result for "+string_no_s+" in Second search original iexact name no S: "+str(counter)
			if counter < 1:
				results = all_rows.filter(name__icontains=string_no_s)
				counter = len(results)
				#print "Result for "+string_no_s+" in 3rd search name_icontains no S: "+str(counter)	
				if counter < 1:
					#Python3: change xrange for range 
					for i in xrange(len(search_list_no_s) - 1, -1, -1):#While iterate going backwards so index continue when removing element
						if len(search_list_no_s[i]) < 3:
							del search_list_no_s[i]
					#search_list = string_no_s.split()
					results = all_rows.filter(reduce(operator.or_, [Q(name__iexact=c) for c in search_list_no_s])).distinct()
					counter = len(results)
					if counter < 1:
						results = all_rows.filter(reduce(operator.or_, [Q(name__icontains=c) for c in search_list_no_s])).distinct()
						counter = len(results)
	return results

def list_search_results_view(request,search=None,page=None):
	alert = ""
	lists_count = 0
	lists_result = List.objects.none()
	if search.strip() != "":
		lists_result = list_search(search)
		lists_count = len(lists_result)
	else:
		#No string in seach, empty
		#Get all the lists
		#lists = List.objects.filter(active=True,private=False)
		lists_result = List.objects.all().prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner__user')
		lists_count = len(lists_result)
		if lists_count == 0:#Brand new database, no list
			search = "*"
	if lists_count > 1:
		paginator = Paginator(lists_result,10)
		try:
			page = int(page)
		except:
			page = 1
		try:
			paginatorlist = paginator.page(page)
		except (EmptyPage, InvalidPage):
			paginatorlist = paginator.page(paginator.num_pages)
		cxt = {'paginatorlist':paginatorlist, 'search':search,}
		return render_to_response('lists_results.html',cxt,context_instance=RequestContext(request))
		#No results, send to seach again
	if lists_count == 0:#0 results
		alert = 1
		request.method = 'GET'
		## 9) Redirect to search with alert ##
		return HttpResponseRedirect('/list_search/%s/%s/'%(search,'1'))
	## 10) Single result? ##
	if lists_count == 1:
		## 11) Redirect to list template ##
		return HttpResponseRedirect('/list/%s/'%(lists_result[0].urlname))

@login_required(login_url=singin_url)
@verified_email_required
def lists_mine_view(request,page=None):
	profile = userProfile.objects.get(user=request.user)
	#lists = List.objects.filter(active=True, owner=profile).order_by('name')
	lists = List.objects.filter(active=True, owner=profile).prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner').order_by('name')
	paginator = Paginator(lists,10)# 20 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist}
	return render_to_response('lists_mine.html',cxt,context_instance=RequestContext(request))
	
def listsfoodie_view(request,username,page=None):
	#print ('look for:'+username)
	foodie = User.objects.get(username=username)
	#profile = userProfile.objects.get(user.username='root')
	profile = userProfile.objects.get(user=foodie)
	#lists = List.objects.filter(active=True, owner=profile, private=False).order_by('name')
	lists = List.objects.filter(active=True, owner=profile).prefetch_related('dishes','dishes__cuisines','listlikes').select_related('owner').order_by('name')
	req_user = request.user
	#print "Total lists: "+str(lists.count())
	# If user authenticated filter its private lists
	if req_user.is_authenticated():
		#User authenticated, hide private list from other users
		req_profile = userProfile.objects.get(user=req_user)
		lists = lists.exclude(~Q(owner = req_profile), type = '3')
		#print "User losggedin, Total lists: "+str(lists.count())
	else:
		# User not authenticated, hide private lists
		lists = lists.exclude(type='3')
		#print "User NOT losgged in, Total lists: "+str(lists.count())
	paginator = Paginator(lists,10)# 20 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist,'profile':profile}
	return render_to_response('lists_foodie.html',cxt,context_instance=RequestContext(request))
#222
def lists_view(request,page=None,alert=None):
	# Alert, sent from list_view when list is private.
	#lists = List.objects.filter(active=True, private=False).annotate(q_likes=Count('listlikes', distinct = True)).order_by('-q_likes')
	lists = List.objects.filter(active=True).prefetch_related('dishes','dishes__cuisines','listlikes').distinct().select_related('owner__user').order_by('-likestot')
	#print "Total lists: "+str(lists.count())
	req_user = request.user
	# If user authenticated filter its private lists
	if req_user.is_authenticated():
		#User authenticated, hide private list from other users
		req_profile = userProfile.objects.get(user=req_user)
		lists = lists.exclude(~Q(owner = req_profile), type = '3')
		#print "User losggedin, Total lists: "+str(lists.count())
	else:
		# User not authenticated, hide private lists
		lists = lists.exclude(type='3')
		#print "User NOT losgged in, Total lists: "+str(lists.count())
	#lists = List.objects.filter(active=True, private=False)
	paginator = Paginator(lists,10)# 20 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist,'alert':alert}
	return render_to_response('lists.html',cxt,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def listedit_view(request,urlname):
	alert = ""
	#print "urlname: "+urlname[:20]
	cxt = {}
	#list = List.objects.get(urlname=urlname)
	try:
		list = List.objects.get(urlname=urlname)
		if list.owner.user != request.user:
		#List doesn't belong to user in the request
			# Is list public?
			if list.type == '2':
				#print "Type 2: "+list.type
				# List is public, send to edit public
				return redirect('view_listedit_public', urlname = urlname)
		# List belong to user request, send edit list private
		return redirect('view_listedit_owner', urlname = urlname)
	# URL Doesn't exist
	except List.DoesNotExist:
		return redirect('view_lists')
	return redirect('view_lists')

@login_required(login_url=singin_url)
@verified_email_required
def listedit_public_view(request,urlname):
	try:
		list = List.objects.get(urlname=urlname)
		if list.owner.user == request.user:
			#List belong to user in the request, redirect to owner view
			#print ("List belong to user in the request, redirect to owner view")
			return redirect('view_listedit_owner', urlname = urlname)
		if (list.owner.user != request.user) and (list.type == '2'):
			# Logged user not owner of list, lists is public
			dishes = ListDish.objects.filter(list=list).order_by('index')
			dishes_counter = dishes.count()
			#print "no post"
			ctx = {'list':list,'dishes':dishes,'total':dishes_counter}
			return render_to_response('list_edit_public.html',ctx,context_instance=RequestContext(request))
		# When user not owner and list is not public
		return redirect('view_lists')
	except List.DoesNotExist:
		return redirect('view_lists')

@login_required(login_url=singin_url)
@verified_email_required
def listedit_owner_view(request,urlname):
	try:
		list = List.objects.get(urlname=urlname)
		if list.owner.user == request.user:
		#List belong to user in the request
			dishes= ListDish.objects.filter(list=list).select_related('list','dish','owner','owner__user').prefetch_related('dish__cuisines').order_by('index')
			dishes_counter = dishes.count()
			if request.method == "POST":
				form = List_Form(request.POST)
				if form.is_valid():
					#print "updating list"
					private = form.cleaned_data['private']
					type = form.cleaned_data['type']
					#print "type: %s, private value: %s" % (type(private),private)
					list.private = private
					#name = form.cleaned_data['name'].strip()
					name = string.capwords(form.cleaned_data['name'].strip())
					list.description = form.cleaned_data['description']
					#Generate urlname
					urlname =  name.lower().replace (" ", "_").replace ("'", "").replace (".", "")
					getKey = List.objects.aggregate(next=Max('id'))['next']
					if getKey >= 1:
						getKey = getKey+1
					else:
						getKey = 1
					if List.objects.filter(urlname = urlname).exclude(id=list.id).count() > 0:
						# at least one object satisfying query exists
						urlname = str(urlname)+'_'+str(getKey)
					else:
						print "same url"
					list.urlname = urlname
					list.name = name
					list.type = type
					list.modified = datetime.now()
					list.save() # Guardar la informacio
					return HttpResponseRedirect('/list/%s/'%(list.urlname))
				else:
					#print "form no valid"
					#print form.errors.as_text
					ctx = {'form':form,'list':list,'dishes':dishes,'total':dishes_counter}
					return render_to_response('list_edit_owner.html',ctx,context_instance=RequestContext(request))
			#print "no post"
			form = List_Form(instance=list)
			ctx = {'form':form,'list':list,'dishes':dishes,'total':dishes_counter}
			return render_to_response('list_edit_owner.html',ctx,context_instance=RequestContext(request))
		else:
			#List doesn't belong to user requesting
			return redirect('view_list', urlname = urlname)
	except List.DoesNotExist:
		return redirect('view_lists')
	
#Templeate: list_edit, Modal that deletes a dish from list
@login_required(login_url=singin_url)
def list_delete_dish_view(request,list_id,dish_id):
	user_logged = request.user
	list = List.objects.get(pk=list_id)
	# Check if user logged is the same as list owner
	if user_logged == user_logged:
		# User logged is owner of list, procede
		dishes_total = ListDish.objects.filter(list=list).count()
		dish_to_delete = ListDish.objects.get(list=list,dish=Dish.objects.get(pk=dish_id))
		idx_del = dish_to_delete.index
		dish_to_delete.delete()
		dishes_list = ListDish.objects.filter(list=list).order_by('index')
		if idx_del < dishes_total:
			for index, d in enumerate(dishes_list):
				d.index = index+1
				d.save()
	return redirect('view_listedit', urlname = list.urlname)
"""
def runit_view(request):
	listdishes = ListDish.objects.all()
	for d in listdishes:
		#print "List:" +str(d.list.id)+"List Owner: "+str(d.list.owner)+" Dish id: "+str(d.id)+" Dishlist Owner: "+str(d.owner)
		d.owner = d.list.owner
		d.save()
	return redirect('view_myprofile')
"""
#Templeate: list_edit, Modal that adds dish to list
@login_required(login_url=singin_url)
def list_add_dish_view(request,list_id,dish_id,url_return):
	user_logged = request.user
	list = List.objects.get(pk=list_id)
	# 1 = Personal:Publicaly available.Only I can add edit
	# 2 = Public: Anybody can edit
	# 3 = Private: Only I can see it
	if (list.type == '1' and user_logged == list.owner.user) or (list.type == '3' and user_logged == list.owner.user) or list.type == '2':
		# list public or sent by owner, proceed to add dish to list
		dishes_total = ListDish.objects.filter(list=list).count()
		listdish = ListDish()
		listdish.list = list
		listdish.dish = Dish.objects.get(pk=dish_id)
		listdish.index = dishes_total+1
		listdish.owner = userProfile.objects.get(user=user_logged)
		listdish.save()
	#print "url_return: "+str(url_return)
	if url_return == 'listeditowner':
		return redirect('view_listedit_owner', urlname = list.urlname)
	if url_return == 'listeditpublic':
		return redirect('view_listedit_public', urlname = list.urlname)
	if url_return == 'list':
		return redirect('view_list', urlname = list.urlname)
	if url_return == 'listedit':
		return redirect('view_listedit', urlname = list.urlname)

@login_required(login_url=singin_url)
@verified_email_required
def listnew_view(request):
	profile = request.user
	if request.method == "POST":
		form = List_Form(request.POST)
		if form.is_valid():
			#name = form.cleaned_data['name'].strip()
			name = string.capwords(form.cleaned_data['name'].strip())
			description = form.cleaned_data['description']
			type = form.cleaned_data['type']
			#private = form.cleaned_data['private']
			d = List()
			d.name = name
			#Generate urlname
			urlname =  name.lower().replace (" ", "_").replace ("'", "").replace (".", "")
			getKey = List.objects.aggregate(next=Max('id'))['next']
			if getKey >= 1:
				getKey = getKey+1
			else:
				getKey = 1
			if List.objects.filter(urlname = urlname).count() > 0:
				# at least one object satisfying query exists
				urlname = str(urlname)+'_'+str(getKey)
			d.urlname = urlname
			#print "urlname: "+str(urlname)
			d.description = description
			#d.private = private
			d.type = type
			d.owner = userProfile.objects.get(user=profile)
			d.created = datetime.now()
			d.modified = datetime.now()
			d.likestot = 0
			d.save()
			return redirect('view_list', urlname = d.urlname)
		else:
			ctx = {'form':form}
			return render_to_response('list_new.html',ctx,context_instance=RequestContext(request))
	form = List_Form()
	ctx = {'form':form}
	return render_to_response('list_new.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def listindexedit_view(request,urlname):
	alert = ""
	cxt = {}
	list = List.objects.get(urlname=urlname)
	#try:
	dishlist = ListDish.objects.filter(list=list).order_by('index')
	if dishlist:#There are dishes
		dishids_list = dishlist.values_list('dish__id', flat=True)
		if request.method == "POST":
			#Get selected dishes with value: "##-####"format, where ##=index, ####=dish_id
			ids = request.POST['indexs']
			list_index  = map(int, ids.split('+'))
			#print list_index
			#print dishids_list
			dishids_list = [dishids_list for (list_index,dishids_list) in sorted(zip(list_index,dishids_list))]
			#print dishids_list
			for i in range(0,len(dishids_list)):
				ListDish.objects.filter(list=list,dish=dishids_list[i]).update(index=i+1)
			list.modified = datetime.now()
			list.save()
			return HttpResponseRedirect('/listedit/%s/'%(list.urlname))
		#print "there is list"
		cxt = {'dishlist':dishlist,'list':list,'dishids_list':dishids_list}
		return render_to_response('listindex_edit.html',cxt,context_instance=RequestContext(request))
	else:
		#There are no dishes go back
		return HttpResponseRedirect('/list/%s/'%(list.urlname))

@login_required(login_url=singin_url)
@verified_email_required
def list_delete_view(request, id):
	user_logged = request.user
	profile_logged = userProfile.objects.get(user=user_logged)
	list = List.objects.get(pk=id)
	if list:
		if profile_logged == list.owner:
			#print str(profile_logged)+" = "+str(list.owner)
			SaveEmailQueue(user_logged.username,'List','Deleted',list.urlname)#Checked
			list.delete()
		else:
			print "you don't own this list"
	else:
		print "there is not list with that id"
	return HttpResponseRedirect('/lists_mine/')
	
#From list.html when updating (dish-list) comments:
@login_required(login_url=singin_url)
def list_dish_comment_update_view(request):
	if request.method == "POST":
		#print('in post')
		form = list_dish_comment_Form(request.POST or None)
		id_list_dish = request.POST.get('id_listdish')
		dish_list = ListDish.objects.get(id=id_list_dish)
		if form.is_valid():
			#print('in form valid')
			id_list_dish = form.cleaned_data['id_listdish']
			#print(str(id_list_dish))
			comment = form.cleaned_data['comments']
			#print(comment)
			dish_list = ListDish.objects.get(id=id_list_dish)
			#print dish_list
			dish_list.description = comment
			dish_list.save()
			#return list_view(request,dish_list.list.urlname)
			return redirect('view_listedit', urlname=dish_list.list.urlname)
		else:
			#print form.errors.as_text
			return list_view(request,dish_list.list.urlname)
	else:
		#print request.method
		return HttpResponseRedirect('/lists/')

#################################
######   P H O T O S      #######
#################################

def photos_view(request):
	info = "Beginning"
	"""
	list_all = Picture.objects.filter(active=True).extra(
		select={
			'num_likes': 'SELECT COUNT(*) FROM files_likepicture WHERE files_likepicture.likes = TRUE AND files_picture.id = files_likepicture.picture_id',
			},
	).order_by('-num_likes')[:100]"""
	list_all = Picture.objects.filter(active=True).order_by('-likestot')[:100]
	ctx = {'information':info,'list':list_all}
	return render_to_response('photos.html',ctx,context_instance=RequestContext(request))

def photofullscreen_view(request, pic_id):
	obj = Picture.objects.get(id=pic_id)
	likes = LikePicture.objects.filter(picture=obj, likes=1).count()
	ctx = {'object':obj, 'likes':likes}
	return render_to_response('photofullscreen.html',ctx,context_instance=RequestContext(request))

def photosfull_view(request):
	info = "Beginning"
	list_all = Picture.objects.filter(active=True).order_by('-likestot')[:100]
	ctx = {'information':info,'list':list_all}
	return render_to_response('photosfull.html',ctx,context_instance=RequestContext(request))

def photouploadmain_view(request):
	return render_to_response('photouploadmain.html',context_instance=RequestContext(request))
#000
@login_required(login_url=singin_url)
@verified_email_required
def photonew_view(request, id):
	info = 0
	form = photoAdd_Form()
	dish = Dish.objects.get(pk=id)
	if request.method == "POST":
		form = photoAdd_Form(request.POST, request.FILES)
		if form.is_valid():
			photo = form.cleaned_data['location']#Esto se obtiene con el request.FILES
			comm = form.cleaned_data['comments']
			ownit = form.cleaned_data['ownit']
			creditsname = form.cleaned_data['creditsname'].strip()
			creditsurl = form.cleaned_data['creditsurl']
			p = Picture()
			print "in photonew_view(), valid form"
			print photo
			if photo:#Generamos validacion
				p.location = photo
			p.comments = comm
			p.ownit = ownit
			p.creditsname = creditsname
			p.creditsurl = creditsurl
			getKey = Picture.objects.aggregate(next=Max('id'))['next']
			p.urlname = str(dish.urlname)+'_'+str(getKey+1)
			#p.likes = 0
			p.datetime = datetime.now()
			p.active = 1
			p.dish = dish
			p.likestot = 0
			req_user = request.user
			profile = userProfile.objects.get(user=req_user)
			p.owner = profile
			p.save() # Guardar la informacion
			info = 2 #Not sure if it is been used
			if not settings.LOCAL_DEV:
				## This is only in production:
				print "Before, p.location: {}".format(p.location)
				loc = str(p.location)
				#dishes_original/bud_light_beer_35.jpg 
				p.location = loc.replace("dishes_original/", "dishes/")
				p.save()
				email_url=request.build_absolute_uri('/')+'photo/%s/'%(p.urlname)
				SaveEmailQueue(req_user.username,'Dish photo','Added',email_url)
				return HttpResponseRedirect('/photo/%s'%(p.urlname))
			else:
				email_url=request.build_absolute_uri('/')+'photo/%s/'%(p.urlname)
				SaveEmailQueue(req_user.username,'Dish photo','Added',email_url)
				## If we are in development, it doesn't need to wait for lambda
				return HttpResponseRedirect('/photo/%s'%(p.urlname))
		else:
			info = 3 #for photonew, information = 3 : Invalid form
			#form = photoAdd_Form(initial={'comments':pic.comments,'ownit':pic.ownit,'creditsname':pic.creditsname,'creditsurl':pic.creditsurl})
			ctx = {'form':form, 'information':info,'dish':dish, 'ownit':form.cleaned_data['ownit']}
			return render_to_response('photonew.html',ctx,context_instance=RequestContext(request))
	form = photoAdd_Form()
	ctx = {'form':form, 'information':info,'dish':dish}
	return render_to_response('photonew.html',ctx,context_instance=RequestContext(request))
	
def photourl_view(request, urlname, reload=None):
	pho = Picture.objects.select_related('dish','owner__user').prefetch_related('dish__cuisines').get(urlname=urlname)
	ind_pho = ""
	prev = ""
	next = ""
	indexes = {}
	#gets the total number of pictures in that dish
	photo_list = Picture.objects.filter(dish=pho.dish).order_by('pk')
	for index, photo in enumerate(photo_list):
		if photo.urlname == urlname:
			ind_pho = index
		indexes[index] = photo.urlname
	if (ind_pho - 1) in indexes:
		prev = indexes[(ind_pho - 1)]
	if (ind_pho + 1) in indexes:
		next = indexes[(ind_pho + 1)]
	##Gets the possition of the index in the list for the Photo 'N' of N
	##Gets the next and previous photo
	liked = 0
	req_user = request.user
	if req_user.is_authenticated():
		req_profile = userProfile.objects.get(user=req_user)
		try:
			obj = LikePicture.objects.get(profile=req_profile, picture=pho)
			if obj.likes == 1:
				liked = 1
		except:
			liked = 0
	cxt = {'object':pho, 'liked':liked, 'reload':reload, 'next':next, 'prev':prev,'photos':len(indexes),'index':ind_pho+1,'MEDIA_URL':settings.MEDIA_URL,'LOADING_IMG':settings.LOADING_IMG}
	return render_to_response('photo.html',cxt,context_instance=RequestContext(request))

def latestphotos_view(request, page=None):
	list_all = Picture.objects.all().order_by('-datetime')
	#list_all = Picture.objects.filter(owner=user.id).order_by('datetime')
	paginator = Paginator(list_all,20)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'list':paginatorlist,'temp':list_all,}
	return render_to_response('latest_photos.html',cxt,context_instance=RequestContext(request))
	
def photo_redirect_view(request,id):
	pho = Picture.objects.get(pk=id)
	return photourl_view(request,pho.urlname)

@login_required(login_url=singin_url)
@verified_email_required
def photocrop_view(request, id):
	info = 0
	photo = Picture.objects.get(pk=id)
	filenamewhole = str(photo.location)[7:]
	filename, ext = os.path.splitext(filenamewhole)
	#med = Image.open(settings.UPLOAD_DISH+'/'+filename+'-med'+photo.extension())
	#w1 = med.width
	#h1 = med.height
	if request.method == "POST":
		form = photoCrop_Form(request.POST)
		if form.is_valid():
			## Form sends the percentage of crop
			x = form.cleaned_data['x']
			y = form.cleaned_data['y']
			w = form.cleaned_data['w']
			h = form.cleaned_data['h']
			print "x: {}%, y: {}% , w: {}%, h: {}%".format(x,y,w,h)
			if settings.LOCAL_DEV:
				print "In photocrop_view local"
				path = str(photo.location.path)
				#print "Rotation: "+str(rotation)
				cad = settings.UPLOAD_DISH + '/'
				#w, h = photo.size
				med_ori = Image.open(cad+filename+'-med'+ext)
				reg_ori = Image.open(cad+filename+'-reg'+ext)
				thum_ori = Image.open(cad+filename+'-thum'+ext)
				max_ori = Image.open(cad+filename+ext)
				sizes={'thum':{'h':thum_ori.height,'w':thum_ori.width},'med':{'h':med_ori.height,'w':med_ori.width},'reg':{'h':reg_ori.height,'w':reg_ori.width},'max':{'h':max_ori.height,'w':max_ori.width},}
				print sizes
				## .crop((left, top, right, bottom))
				#max_new = max_ori.crop((x*3,y*3,w*3+x*3,h*3+y*3))
				max_new = max_ori.crop((
					int(round(sizes['max']['w']*x/100)),
					int(round(sizes['max']['h']*y/100)),
					int(round(sizes['max']['w']*w/100)) + int(round(sizes['max']['w']*x/100)) ,
					int(round(sizes['max']['h']*h/100)) + int(round(sizes['max']['h']*y/100))
					))
				max_new.save(cad+filename+ext)
				
				#thum_new = thum_ori.crop((x/4,y/4,w/4+x/4,h/4+y/4))
				thum_new = thum_ori.crop((
					int(round(sizes['thum']['w']*x/100)) ,
					int(round(sizes['thum']['h']*y/100)) ,
					int(round(sizes['thum']['w']*w/100)) + int(round(sizes['thum']['w']*x/100)) ,
					int(round(sizes['thum']['h']*h/100)) + int(round(sizes['thum']['h']*y/100))
					))
				thum_new.save(cad+filename+'-thum'+ext)

				#med_new = med_ori.crop((x,y,w+x,h+y))
				med_new = med_ori.crop((
					int(round(sizes['med']['w']*x/100)) ,
					int(round(sizes['med']['h']*y/100)),
					int(round(sizes['med']['w']*w/100)) + int(round(sizes['med']['w']*x/100)),
					int(round(sizes['med']['h']*h/100)) + int(round(sizes['med']['h']*y/100))
					))
				med_new.save(cad+filename+'-med'+ext)

				#reg_new = reg_ori.crop((x*2,y*2,w*2+x*2,h*2+y*2))
				reg_new = reg_ori.crop((
					int(round(sizes['reg']['w']*x/100)) ,
					int(round(sizes['reg']['h']*y/100)) ,
					int(round(sizes['reg']['w']*w/100)) + int(round(sizes['reg']['w']*x/100)) ,
					int(round(sizes['reg']['h']*h/100)) + int(round(sizes['reg']['h']*y/100))
					))
				reg_new.save(cad+filename+'-reg'+ext)

				if h > w:
					thum_wsize = int(sizes['thum']['h']*thum_new.width/thum_new.height)
					thum = thum_new.resize((thum_wsize,int(sizes['thum']['h'])), Image.ANTIALIAS)
					thum.save(cad+filename+'-thum'+ext)
					
					med_wsize = int(sizes['med']['h']*med_new.width/med_new.height)
					med = med_new.resize((med_wsize,int(sizes['med']['h'])), Image.ANTIALIAS)
					med.save(cad+filename+'-med'+ext)
					
					reg_wsize = int(sizes['reg']['h']*reg_new.width/reg_new.height)
					reg = reg_new.resize((reg_wsize,int(sizes['reg']['h'])), Image.ANTIALIAS)
					reg.save(cad+filename+'-reg'+ext)
					
					max_wsize = int(sizes['max']['h']*max_new.width/max_new.height)
					max = max_new.resize((max_wsize,int(sizes['max']['h'])), Image.ANTIALIAS)
					max.save(cad+filename+ext)
				else:
					thum_hsize = int(thum_new.height*sizes['thum']['w']/thum_new.width)
					thum = thum_new.resize((int(sizes['thum']['w']),thum_hsize), Image.ANTIALIAS)
					thum.save(cad+filename+'-thum'+ext)
					
					med_hsize = int(med_new.height*sizes['med']['w']/med_new.width)
					med = med_new.resize((int(sizes['med']['w']),med_hsize), Image.ANTIALIAS)
					med.save(cad+filename+'-med'+ext)
					
					reg_hsize = int(reg_new.height*sizes['reg']['w']/reg_new.width)
					reg = reg_new.resize((int(sizes['reg']['w']),reg_hsize), Image.ANTIALIAS)
					reg.save(cad+filename+'-reg'+ext)
					
					max_hsize = int(max_new.height*sizes['max']['w']/max_new.width)
					max = max_new.resize((int(sizes['max']['w']),max_hsize), Image.ANTIALIAS)
					max.save(cad+filename+ext)
			else:
				#print "In photocrop_view production"
				import boto3
				bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
				payload = {"bucket":bucket, "filename":filename, "ext":ext, "x":x, "y":y, "w":w, "h":h}
				#print "filename: {}, ext: {}".format(payload['filename'],payload['ext'])
				client = boto3.client('lambda',
					region_name= 'us-west-2',
					aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
					aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
				#000
				## If original file exists, work with it
				## Because photos migrated from Webfation won't have original images in dishes_original folder
				## We only trigger 
				media_url = os.environ.get('MEDIA_URL_AWS')#This will get: https://wfgp.s3-us-west-2.amazonaws.com/media or wfgs
				photopath = "{}/dishes_original/{}{}".format(media_url,filename, ext)
				import requests
				request = requests.get(photopath)
				if request.status_code == 200:
					#print "photo original exists!"
					FuncName = "wfgOriginalPhotoCrop"
				else:
					FuncName = "wfgPhotoCrop"
					##Photo original doesn't exists, work with thumbs
					# create lambda client
					print "photo original Doesn't exists!"
				result = client.invoke(FunctionName=FuncName,
					InvocationType='RequestResponse',                                      
					Payload=json.dumps(payload))
				#range = result['photoid']
				print "Finishes lambda"
				print result
			return HttpResponseRedirect('/photo/%s/%d/'%(photo.urlname,1))
	form = photoCrop_Form()
	#ctx = {'form':form, 'information':info,'photo':photo,'w1':w1,'h1':h1}
	ctx = {'form':form, 'information':info,'photo':photo}
	return render_to_response('photocrop.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def photorotate_view(request, id):
	info = 0
	photo = Picture.objects.get(pk=id)
	#print "begining"
	if request.method == "POST":
		form = photoRotate_Form(request.POST)
		if form.is_valid():
			rotation = form.cleaned_data['rotation']
			filenamewhole = str(photo.location)[7:]
			filename, ext = os.path.splitext(filenamewhole)
			if settings.LOCAL_DEV:
				path = str(photo.location.path)
				print "In photorotate_view local"
				#print "Rotation: "+str(rotation)
				cad = settings.UPLOAD_DISH + '/'

				main_1 = Image.open(path)
				main_2 = main_1.rotate(rotation, expand=1)
				main_2.save(path)

				reg_1 = Image.open(cad+filename+'-reg'+ext)
				reg_2 = reg_1.rotate(rotation, expand=1)
				reg_2.save(cad+filename+'-reg'+ext)

				med_1 = Image.open(cad+filename+'-med'+ext)
				med_2 = med_1.rotate(rotation, expand=1)
				med_2.save(cad+filename+'-med'+ext)

				thum_1 = Image.open(cad+filename+'-thum'+ext)
				thum_2 = thum_1.rotate(rotation, expand=1)
				thum_2.save(cad+filename+'-thum'+ext)

			else:
				print "In photorotate_view production"
				path = str(photo.location.url)
				# create lambda client
				import boto3
				payload = {"filename":filename, "ext":ext, "rotation":rotation}
				print "filename: {}, ext: {}, rotation: {} ".format(payload['filename'],payload['ext'],payload['rotation'])
				client = boto3.client('lambda',
					region_name= 'us-west-2',
					aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
					aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
				result = client.invoke(FunctionName='rotateImage',
                    InvocationType='RequestResponse',                                      
                    Payload=json.dumps(payload))
				#range = result['photoid']
				print "Finishes lambda"
				print result
		return HttpResponseRedirect('/photo/%s/%d/'%(photo.urlname,1))
			
	form = photoRotate_Form()
	ctx = {'form':form, 'information':info,'photo':photo}
	return render_to_response('photorotate.html',ctx,context_instance=RequestContext(request))

def photolike_view(request):
	profile1 = userProfile.objects.get(pk=request.user.pk)
	likes_tot = "like"
	if request.method == "GET":
		id_photo = request.GET['photo']
		photo = Picture.objects.get(id=id_photo)
		obj, created = LikePicture.objects.get_or_create(profile=profile1, picture=photo, defaults={'likes': True})
		obj.likes = 1
		obj.save()
		likes_tot = LikePicture.objects.filter(picture=photo, likes=1).count()
		return HttpResponse(likes_tot)

def photounlike_view(request):
	profile1 = userProfile.objects.get(pk=request.user.pk)
	likes_tot = "unlike"
	if request.method == "GET":
		id_photo = request.GET['photo']
		photo = Picture.objects.get(id=id_photo)
		obj = LikePicture.objects.get(profile=profile1, picture=photo)
		obj.likes = 0
		obj.save()
		likes_tot = LikePicture.objects.filter(picture=photo, likes=1).count()
		return HttpResponse(likes_tot)

@login_required(login_url=singin_url)
@verified_email_required
def photoedit_view(request, id):
	info = 0
	pic = Picture.objects.get(pk=id)
	if pic.owner.user == request.user:
		# picture owner is the same as user request, it is ok to edit
		form = photoEdit_Form()
		likes_tot = LikePicture.objects.filter(picture=pic, likes=1).count()
		if request.method == "POST":
			form = photoEdit_Form(request.POST)
			if form.is_valid():
				comm = form.cleaned_data['comments']
				ownit = form.cleaned_data['ownit']
				creditsname = form.cleaned_data['creditsname']
				creditsurl = form.cleaned_data['creditsurl']
				pic.ownit = ownit
				pic.creditsname = creditsname
				pic.creditsurl = creditsurl
				pic.comments = comm
				pic.save() # Guardar la informacion
				ctx = {'form':form, 'information':info}
				return HttpResponseRedirect('/photo/%s'%(pic.urlname))
		form = photoEdit_Form(initial={'comments':pic.comments,'ownit':pic.ownit,'creditsname':pic.creditsname,'creditsurl':pic.creditsurl})
		ctx = {'form':form, 'information':info,'object':pic, 'likestotal':likes_tot}
		return render_to_response('photoedit.html',ctx,context_instance=RequestContext(request))
	else:
		#Photo doesn't belong to user requesting
		return redirect('view_photourl', urlname = pic.urlname)

@login_required(login_url=singin_url)
@verified_email_required
def photodelete_view(request, id):
	info = 0
	photo = Picture.objects.get(pk=id)
	dish = photo.dish
	if request.method == "POST":
		if settings.LOCAL_DEV:
			## Remove files locally
			ruta = str(photo.location.path)
			urlname = str(photo.urlname)
			ext = str(photo.extension())
			if os.path.exists(ruta):
				os.remove(ruta)
			if os.path.exists(settings.UPLOAD_DISH+"/"+urlname+"-med"+ext):
				os.remove(settings.UPLOAD_DISH+"/"+urlname+"-med"+ext)
			if os.path.exists(settings.UPLOAD_DISH+"/"+urlname+"-reg"+ext):
				os.remove(settings.UPLOAD_DISH+"/"+urlname+"-reg"+ext)
			if os.path.exists(settings.UPLOAD_DISH+"/"+urlname+"-thum"+ext):
				os.remove(settings.UPLOAD_DISH+"/"+urlname+"-thum"+ext)
		else:
			## Remove files in the  bucket
			import boto3
			s3 = boto3.resource('s3')
			bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
			basename = os.path.basename(photo.location.url)
			filename, extension = os.path.splitext(basename)
			print "basename: {}, filename: {}, extension: {} ".format(basename, filename, extension)
			key = 'media/dishes/{}{}'.format(filename, extension)
			key_reg = 'media/dishes/{}-reg{}'.format(filename, extension)
			key_med = 'media/dishes/{}-med{}'.format(filename, extension)
			key_thum = 'media/dishes/{}-thum{}'.format(filename, extension)
			key_original = 'media/dishes_original/{}{}'.format(filename, extension)
			key_deleted = 'media/dishes_deleted/{}{}'.format(filename, extension)
			print "key: {}, key_reg: {}, key_med: {} ".format(key, key_reg, key_med)
			try:
				s3.Object(bucket,key).delete()
			except:
				pass
			try:
				s3.Object(bucket,key_reg).delete()
			except:
				pass
			try:
				s3.Object(bucket,key_med).delete()
			except:
				pass
			try:
				s3.Object(bucket,key_thum).delete()
			except:
				pass
			# Moving original file to dishes_delete folder
			try:
				s3.Object(bucket,key_deleted).copy_from(CopySource='wfgs/'+key_original)
			except:
				pass
			try:
				s3.Object(bucket,key_original).delete()
			except:
				pass
		SaveEmailQueue(request.user.username,'Photo','Deleted',photo.urlname)
		photo.delete()
		UpdateMainPhoto(dish.pk)
		return HttpResponseRedirect('/dish/%s'%(dish.urlname))
	ctx = {'information':info, 'photo':photo}
	return render_to_response('photodelete.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
@verified_email_required
def photos_mine_view(request, page=None):
	profile = userProfile.objects.get(pk=request.user.pk)
	#user = User.objects.get(username=username)
	
	#req_user = request.user
	#req_profile = userProfile.objects.get(user=req_user)
	#obj = LikePicture.objects.get(profile=req_profile, picture=pho)

	#list_all = Picture.objects.filter(owner=user.id).select_related('dish','owner','owner__user').prefetch_related('dish__cuisines').order_by('dish')
	list_all = Picture.objects.filter(owner=profile).select_related('dish','owner','owner__user').prefetch_related('dish__cuisines').order_by('dish')
	paginator = Paginator(list_all,20)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	#cxt = {'list':paginatorlist,'profile':user,'temp':list_all,}
	cxt = {'list':paginatorlist,'profile':profile.user,'temp':list_all,}
	return render_to_response('userphotos.html',cxt,context_instance=RequestContext(request))
	
#################################
######   S E A R C H      #######
#################################

def searchquick_view(request):
	if request.method == "POST":
		form = search_Form(request.POST or None)
		if form.is_valid():
			search = form.cleaned_data['search']
			source = form.cleaned_data['source']
			search = search.strip()#Removes beginning and ending blanks
			search = unicodedata.normalize('NFKD', search).encode('ASCII', 'ignore')#converts: naïve café -> naive cafe
			req_user = request.user
			#Store seach words in SearchLog if not me
			if req_user.is_authenticated():
				if req_user.username != 'itisclaudio':
					new_search = SearchLog()
					profile = userProfile.objects.get(user=req_user)
					new_search.foodie = profile
					new_search.datetime = datetime.now()
					new_search.search_origin = source
					new_search.searchwords = search
					new_search.save()
			else:
				new_search = SearchLog()
				new_search.datetime = datetime.now()
				new_search.search_origin = source
				new_search.searchwords = search
				new_search.save()
			if len(search) > 2:
				return HttpResponseRedirect(reverse('view_searchquickres', args=('0',search,'1')))
				#searchquickres_view(request,alert=None,search=None,page=None):
			else:
				search = ''
	#return redirect('searchadvance_view')
	return searchadvance_view(request)

def dish_search(string_sent):
	#print "--------------in dish_search()--------------"
	#string_stripped = string_sent.strip()
	string_stripped = ' '.join(string_sent.split())#Removes any multiple spaces
	#print str(string_stripped)
	dish_count = 0
	dishes_result = Dish.objects.none()
	if string_stripped:#If string is not empty
		#print "Si hay string_stripped"
		#Searches exact string, spaces cleared
		all_dishes = Dish.objects.filter(active=True).select_related('userprofile__user').prefetch_related('cuisines').annotate(Count('picture'))
		#all_dishes = Dish.objects.filter(active=True)
		dishes_result = all_dishes.filter(Q(name__iexact=string_stripped) | Q(othernames__iexact=string_stripped))
		dishes_count = len(dishes_result)
		#print "Dishes with iexact in name and othernames: "+str(dishes_count)
		if dishes_count < 1:
		#search commpleate frace in othernames with commas
			#print "No dishes with iexact in name and othernames. Will search icontains in othernames"
			list_with_commas = []
			list_with_commas.append(", "+string_stripped)
			list_with_commas.append(","+string_stripped)
			list_with_commas.append(string_stripped+",")
			list_with_commas.append(string_stripped+" ,")
			#dishes_result = all_dishes.filter((othernames__icontains=c) for c in list_with_commas)
			dishes_result = all_dishes.filter(reduce(operator.or_, [Q(othernames__iexact=c) for c in list_with_commas]))
			dishes_count = len(dishes_result)
			#print "Searching: "
			#print list_with_commas
			#print "with iexact in othernames using or, resulst: "+str(dishes_count)
			if dishes_count < 1:
				#Search commplete frace in names and othernames with no S at the end of words
				#print "no results for -"+str(string_stripped)+"-, in first stage: Exact frace, spaces cleared. Now clearing S"
				string_no_s = ' '.join([item.rstrip('s') for item in string_stripped.split()])
				#Searches exact string, S cleared
				dishes_result = all_dishes.filter(Q(name__iexact=string_no_s) | Q(othernames__iexact=string_no_s))
				dishes_count = len(dishes_result)
				#print "Dishes with iexact in name and othernames with S cleared: "+str(dishes_count)
				if dishes_count < 1:
					#Search combination of words with spaces in name and othernames
					#clears words with less than 3 letters, so it doesn't look for 'of' 'a', etc
					#print "no results for -"+str(string_no_s)+"-, in second stage: Exact frace, S cleared, now combine words"
					search_list = string_no_s.split()
					#Python3: change xrange for range
					AVOID_3 = ('con','del',)
					for i in xrange(len(search_list) - 1, -1, -1):#While iterate going backwards so index continue when removing element
						if len(search_list[i]) < 3 or search_list[i].lower() in AVOID_3:
							del search_list[i]
					#print "Will search iexact in name and othernames from list:"
					#print search_list
					dishes_result = all_dishes.filter(reduce(operator.and_, [Q(name__iexact=c)|Q(othernames__iexact=c) for c in search_list]))
					dishes_count = len(dishes_result)
					#print "Results with combined words using and_, iexact: "+str(dishes_count)
					#print dishes_result
					if dishes_count < 1:
						dishes_result = all_dishes.filter(reduce(operator.and_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in search_list]))
						dishes_count = len(dishes_result)
						#print "Results with combined words using icontains: "+str(dishes_count)					
						if dishes_count < 1:
							#Adding spaces to words 
							#search_list = [" "+word for word in search_list]
							list_blank_left = [" "+word for word in search_list]
							list_blank_right = [word+" " for word in search_list]
							list_with_blanks = list_blank_left + list_blank_right
							#print "Searching icontains for names and othernames from list with blanks:"
							#print list_with_blanks
							#Searcheed one word
							dishes_result = all_dishes.filter(reduce(operator.or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in list_with_blanks]))
							dishes_count = len(dishes_result)
							#print "Results with combined words: "+str(dishes_count)
	return dishes_result

def searchquickres_view(request,alert=None,search=None,page=None):
	#print "---------in searchquickres_view()---------------"
	cui_count = 0 #result counter for cuisines
	dish_count = 0 #result counter for dishes
	lists_count = 0 #result counter for lists
	results_count = 0 #counter for all results
	dishes_result = dish_search(search)
	dish_count = len(dishes_result)
	#search = search.rstrip('s')
	if (len(search) > 2):#at least 3 character, look also for cuisines and lists
		#search = unicodedata.normalize('NFKD', search).encode('ASCII', 'ignore')#converts: naïve café -> naive cafe
		search_list_before = search.split()
		search_list = [item.rstrip('s') for item in search_list_before]
		### cuisine search NEW ###
		cuisine_result = cuisine_search(search)
		cui_count = len(cuisine_result)
		#print "cuisine results: "+str(cui_count)
		#List search
		#NEW:
		### lists search ###
		lists_result = list_search(search)
		lists_count = len(lists_result)
		#print "list result: "+str(lists_count)
		results_count = dish_count + cui_count + lists_count
		if results_count == 1:
			#The means only one cuisine or one dish or one list
			if len(dishes_result) == 1:
				return HttpResponseRedirect('/dish/%s/'%(dishes_result[0].urlname))
			if len(cuisine_result) == 1:
				return HttpResponseRedirect('/cuisine/%s/'%(cuisine_result[0].urlname))
			if lists_count == 1:
				return HttpResponseRedirect('/list/%s/'%(lists_result[0].urlname))
		else:#results more than 1
			if results_count > 1:
				cxt = {'cuisines':cuisine_result,'cui_count':cui_count,'dishes':dishes_result, 'lists':lists_result,'list_count':lists_count,'results':results_count,'search':search}
				#print "going to searchresults.html"
				return render_to_response('searchresults.html',cxt,context_instance=RequestContext(request))
				#return HttpResponseRedirect(reverse('searchquickres_view'))
	else:
		if search != "*" and search != "":
			#Searching in dishes since it is 1 or 2 characters
			dishes_result = dishes_result.filter(Q(name__icontains=search) | Q(othernames__icontains=search))
			results_count = results_count + len(dishes_result)
		else:
			results_count = results_count + len(dishes_result)
			search= "*"
	if results_count == 0:#0 results_count
		#print "in results_count == 0"
		alert = 1
		#Clear seach variable if it is not alphanumeric
		if not all(x.isalnum() or x.isspace() for x in search):
			search= "*"
		return HttpResponseRedirect('/searchadvance/%s/%s/%s/%s/%s/'%('1',search,'*','*',1))
	### 9-Render template ###
	#Clear seach variable if it is not alphanumeric
	if not all(x.isalnum() or x.isspace() for x in search):
		search= "*"
	paginator = Paginator(dishes_result,20)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist, 'search':search,'all_dishes':dishes_result,}
	#print "going to searchquick.html"
	return render_to_response('searchquick.html',cxt,context_instance=RequestContext(request))

def searchadvance_view(request,alert=None,names=None,ingredients=None,cuisines=None,page=None):
	cuisine_list = None
	cui = Cuisine.objects.all()
	names_string=ingredients_string=cui_string=""
	if request.method == "POST" and alert != 0:
		form = searchAdvance_Form(request.POST or None)
		if form.is_valid():
			names = form.cleaned_data['names']
			ingredients = form.cleaned_data['ingredients']
			cuisine_dict = form.cleaned_data['cuisines']
			names = names.strip()
			names = unicodedata.normalize('NFKD', names).encode('ASCII', 'ignore')#converts: naïve café -> naive cafe
			if names:
				names_list = names.lower().split(',')
				names_list = [line.strip() for line in names_list]
				names_string = '+'.join(names_list)
			if ingredients:
				ingredients_list = ingredients.lower().split(',')
				ingredients_list = [line.strip() for line in ingredients_list]
				singularized_list = []
				for i in ingredients_list:
					singularized_list.append(singularize(i))
				ingredients_string = '+'.join(singularized_list)
			cuisines_list = []
			if len(cuisine_dict) > 0:
				for e in cuisine_dict.all():
					cuisines_list.append(str(e.id))
				cui_string = '+'.join(cuisines_list)
			#Store seach words in SearchLog if not me
			req_user = request.user
			if req_user.is_authenticated():
				if req_user.username != 'itisclaudio':
					new_search = SearchLog()
					profile = userProfile.objects.get(user=req_user)
					new_search.foodie = profile
					new_search.datetime = datetime.now()
					new_search.search_origin = request.path
					new_search.searchwords = names_string+ingredients_string+cui_string
					new_search.save()
			else:
				new_search = SearchLog()
				new_search.datetime = datetime.now()
				new_search.search_origin = request.path
				new_search.searchwords = names_string+ingredients_string+cui_string
				new_search.save()
			#searchresultadv_view(request , name1+name2 , ing1+ing2 , 2+3+10 , 1)
			## Validate that the string has at least 3 characters
			if len(names) < 3:
				names = ''
			return searchresultadv_view(request,names_string,ingredients_string,cui_string,1)
	if alert == 1:
		if names != "*" and names != "":
			names_list = names.split('+')
			names_string =  names.replace ("+", ", ")
		else:
			names = '*'
		if ingredients != "*" and ingredients != "":
			ingredients_string =  ingredients.replace ("+", ", ")
		else:
			ingredients =  '*'
		if cuisines != "*" and cuisines != "":
			cuisines_list = cuisines.split('+')
			cuisines_obj = cui.filter(pk__in=cuisines_list)
			cuisines_name_list = []
			for e in cuisines_obj.all():
				cuisines_name_list.append(str(e.name))
			cui_string = ', '.join(cuisines_name_list)
		else:
			cuisines = "*"
	form = searchAdvance_Form()
	cxt = {'form':form,'alert':alert, 'names':names,'ingredients':ingredients,'cuisines':cuisines,'names_string':names_string,'ingredients_string':ingredients_string,'cuisines_string':cui_string}
	return render_to_response('searchadvance.html',cxt,context_instance=RequestContext(request))

def search_advance(names_string=None, cuisines_ids=None, ingredients_string=None):
	###search_advence(dish name, 1+4+6, rice+potato ):
	### '*' are necesary to pass as 'all' in pagination, url doesn't take blank as wildcard
	#print "in searchdish"
	#string_stripped = string_sent.strip()
	cuisines_string = "*"
	names_string = ' '.join(names_string.split())#Removes any multiple spaces
	#print str(names_string)
	dish_count = 0
	dishes_result = Dish.objects.none()
	#all_dishes = Dish.objects.filter(active=True).select_related('userprofile__user').prefetch_related('cuisines').annotate(Count('picture'))
	all_dishes = Dish.objects.all()
	if cuisines_ids != "*" and cuisines_ids != "":
		# print "There are cuisines: "
		# print type(cuisines_ids)
		# print cuisines_ids
		cuisines_ids_list = cuisines_ids.split('+')
		cuisines_q = Cuisine.objects.filter(pk__in=cuisines_ids_list).values_list('name', flat=True)
		cuisines_names_list = list(cuisines_q)
		cuisines_string = ', '.join(cuisines_names_list)
		# print cuisines_names_list
		# print "This should be list:"
		# print type(cuisines_names_list)
		# print type(cuisines_ids_list)
		# print cuisines_ids_list
		#cuisines_obj = Cuisine.objects.filter(pk__in=cuisines_ids_list)
		## 3) Filter cuisines ##
		all_dishes = all_dishes.filter(cuisines__in=cuisines_ids_list)
		#dishes_result = all_dishes
		#print dishes_result
	else:
		#print "no cuisines, all_dishes.all"
		cuisines_ids = "*"
		cuisines_string = "*"
	dishes_result = all_dishes
	if names_string != "*" and names_string != "":
		#print "Si hay names"
		#print names_string
		#Searches exact string, spaces cleared
		#all_dishes = Dish.objects.filter(active=True)
		dishes_result = all_dishes.filter(Q(name__iexact=names_string) | Q(othernames__iexact=names_string))
		# print "after name__iexact=names_string | othernames__iexact=string_strippe:"
		# print dishes_result
		dishes_count = len(dishes_result)
		if dishes_count < 1:
		#search commpleate frace in othernames with commas
			list_with_commas = []
			list_with_commas.append(", "+names_string)
			list_with_commas.append(","+names_string)
			list_with_commas.append(names_string+",")
			list_with_commas.append(names_string+" ,")
			#print "now searching in othernames for: "
			#print list_with_commas
			#dishes_result = all_dishes.filter((othernames__iexact=c) for c in list_with_commas)
			dishes_result = all_dishes.filter(reduce(operator.or_, [Q(othernames__iexact=c) for c in list_with_commas]))
			dishes_count = len(dishes_result)
			if dishes_count < 1:
				#Search commpleate frace in othernames with commas and no S at the end of words
				#print "no results for -"+str(names_string)+"-, in first stage: Exact frace, spaces cleared"
				string_no_s = ' '.join([item.rstrip('s') for item in names_string.split()])
				#Searches exact string, S cleared
				dishes_result = all_dishes.filter(Q(name__iexact=string_no_s) | Q(othernames__iexact=string_no_s))
				dishes_count = len(dishes_result)
				#print dishes_result
				if dishes_count < 1:
					#Search combination of words with spaces in name and other names
					#clears words with less than 3 letters, so it doesn't look for 'of' 'a', etc
					#print "no results for -"+str(string_no_s)+"-, in second stage: Exact frace, S cleared"
					search_list = string_no_s.split()
					#Python3: change xrange for range 
					for i in xrange(len(search_list) - 1, -1, -1):#While iterate going backwards so index continue when removing element
						if len(search_list[i]) < 4:
							del search_list[i]
					dishes_result = all_dishes.filter(reduce(operator.or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in search_list]))
					dishes_count = len(dishes_result)
					#print dishes_result
					if dishes_count < 1:
						search_list = [" " +word for word in search_list]
						list_blank_left = [" " +word for word in search_list]
						list_blank_right = [word+" " for word in search_list]
						list_with_blanks = list_blank_left + list_blank_right
						#Searcheed one word
						dishes_result = all_dishes.filter(reduce(operator.or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in list_with_blanks]))
	else:
		#print "No names given"
		#names_string = "Any"
		names_string = "*"
	#if ingredients_string:#If there are ingredientes
	if ingredients_string != "*" and ingredients_string != "":
		#print "Si hay ingredients_string"
		#print ingredients_string
		ingredients_list = ingredients_string.split('+')
		#Searches exact string, spaces cleared
		#all_dishes = Dish.objects.filter(active=True)
		#results = results.filter(reduce(and_, [Q(ingredients__icontains=c) for c in ingredients_list])).distinct()
		dishes_result = dishes_result.filter(reduce(and_, [Q(ingredients__icontains=c) for c in ingredients_list])).distinct()
		#print "after first ingredients search:"
		#print dishes_result
		dishes_count = len(dishes_result)
	else:
		ingredients_string = "*"
		#print "no ingredients"
	#string = "Names: "+names_string+" | Ingredients: "+ingredients_string.replace ("+", " ,")+" | Cuisines: "+cuisines_string
	strings = {'name_url':names_string, 'ingredients_url':ingredients_string, 'cuisines_url':cuisines_ids,'name_str':names_string,'ingredients_str':ingredients_string.replace ("+", " ,"),'cuisines_str':cuisines_string}
	return dishes_result, strings


def searchresultadv_view(request,names=None,ingredients=None,cuisines=None,page=None):
	###search_advence(dish name, 1+4+6, rice+potato ):
	results, strings = search_advance(names,cuisines,ingredients)
	#print "In searchresultadv_view"
	#print strings
	names_string=ingredients_string=cuisines_string=""
	results_count = len(results)
	## 8) Cero results? ##
	if results_count == 0:#0 results
		alert = '1'#Show alert "no results for your search, search again"
		request.method = 'GET'
		## 9) Redirect to search with alert ##
		#return HttpResponseRedirect('/searchadvance/%s/%s/%s/%s/%s'%('1',names_string,ingredients_string,cuisines_string,1))
		#return HttpResponseRedirect('/searchadvance/%s/%s/%s/%s/%s'%('1',names,ingredients,cuisines,1))
		return searchadvance_view(request,'1',strings['name_str'],strings['ingredients_str'],strings['cuisines_str'],'')
	## 10) Single result? ##
	if results_count == 1:
		## 11) Redirect to dish template ##
		return HttpResponseRedirect('/dish/%s/'%(results[0].urlname))
	### 12) Render results to template ###
	
	paginator = Paginator(results,20)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist, 'names':strings['name_url'],'ingredients':strings['ingredients_url'],'cuisines':strings['cuisines_url'],'names_string':strings['name_str'],'ingredients_string':strings['ingredients_str'],'cuisines_string':strings['cuisines_str']}
	return render_to_response('searchresultsadv.html',cxt,context_instance=RequestContext(request))

#######################################
##########    A J A X       ###########
#######################################

#Used in dish to added to list
@login_required(login_url=singin_url)
@verified_email_required
def lists_autocomplete_view(request):
	if request.is_ajax:
		#print ("request is ajax")
		string_in = request.GET.get('term','')
		string_in = string_in.strip()
		objs = List.objects.filter(Q(name__icontains=string_in),active=True).distinct()
		#dishes = Dish.objects.filter(Q(name__icontains=string_in) | Q(othernames__icontains=string_in)| Q(cuisines__name__icontains=string_in),active=True).distinct()
		results=[]
		for list in objs:
			# Ask if list is not private or (list is private AND user autenticated is owner)
			if list.type == '2' or (list.type != '2' and list.owner.user == request.user):
				list_json={}
				#label=list.name[:20]
				if len(list.name) > 40:
					label=list.name[:40]+"..."
				else:
					label=list.name
				if list.dishes:
					inx = 1
					for dish in list.dishes.all():
						inx += 1
						if len(dish.name) > 10:
							label += " ("+dish.name[:10]+"..)"
						else:
							label += " ("+dish.name+")"
						if inx == 4:
							label += "(...)"
							break
				list_json['value']= list.id
				list_json['label']= label
				results.append(list_json)
		data_json=json.dumps(results)
	else:
		data_json='fail'
	mimetype="application/json"
	return HttpResponse(data_json,mimetype)

# Used in photo new no dish, update, list, related dish in dish (add new dish modal)
def dishlist_view(request, id_dish=None):
	if request.is_ajax:
		#print ("request is ajax")
		string_in = request.GET.get('term','')
		string_in = string_in.strip()
		string_in = string_in.rstrip('s')
		if id_dish:
			dishes = Dish.objects.filter(Q(name__icontains=string_in) | Q(othernames__icontains=string_in)| Q(cuisines__name__icontains=string_in),active=True).exclude(pk=id_dish).distinct()
		else:
			dishes = Dish.objects.filter(Q(name__icontains=string_in) | Q(othernames__icontains=string_in)| Q(cuisines__name__icontains=string_in),active=True).distinct()
		results=[]
		#print dishes
		for dish in dishes:
			dish_json={}
			label=dish.name
			if dish.othernames:
				label += ", "+dish.othernames
			if dish.cuisines:
				inx = 1
				for cui in dish.cuisines.all():
					inx += 1
					label += " ("+cui.name+")"
					if inx == 4:
						label += "..."
						break
			dish_json['value']=dish.id
			dish_json['label']=label
			results.append(dish_json)
		data_json=json.dumps(results)
	else:
		data_json='fail'
	mimetype="application/json"
	return HttpResponse(data_json,mimetype)

#Used in photo new no dish, update
# Check if still needed 
def ajax_autocom_dishes1_view(request):
	"""
	Receives a string from template and returns a json with
	dishes that contain the string in their name and othernames
	with the formant ({value:id}, {label:names, othernames, (cuisines,..)})"""
	if request.is_ajax:
		#print ("request is ajax")
		string_in = request.GET.get('term','')
		dishes = Dish.objects.filter(Q(name__icontains=string_in) | Q(othernames__icontains=string_in),active=True).distinct()
		results=[]
		for dish in dishes:
			dish_json={}
			label=dish.name
			if dish.othernames:
				label += ", "+dish.othernames
			if dish.cuisines:
				inx = 1
				for cui in dish.cuisines.all():
					inx += 1
					label += " ("+cui.name+")"
					if inx == 4:
						label += "..."
						break
			dish_json['value']=dish.id
			dish_json['label']=label
			results.append(dish_json)
		data_json=json.dumps(results)
	else:
		data_json='fail'
	mimetype="application/json"
	return HttpResponse(data_json,mimetype)

def ajax_getlist_view(request):
	#Receives a list id and returns json with list data
	if request.method == "GET":
		id = request.GET['id']
		d = {}#create a list
		if id != "":
			list = List.objects.get(pk=id)
		if list:
			dish_dic = {}
			for dish in list.dishes.all()[:20]:
				dish_dic[dish.id] = dish.name
			d = {'id':list.id,'name':list.name, 'urlname':list.urlname, 'description':list.description, 'dishes':dish_dic}
			#print dish_dic
			data = json.dumps(d)
		else:
			data = "0"
		return HttpResponse(data, content_type="application/json")
	
def ajax_getdish_view(request):
	#Receives a dish id and returns json with dish data
	if request.method == "GET":
		id = request.GET['id']
		d = {}#create a list
		favphoto = "0"
		if id != "":
			dish = Dish.objects.get(pk=id)
			#print dish
		if dish:
			#print dish
			cui_dic = {}
			#dishes_query = Cuisine.objects.filter(name=nami)
			#for cui in dish.cuisines.all():
			#	cui_dic[cui.id] = cui.name
			#if dish.cuisines.all():
			inx = 1
			for cui in dish.cuisines.all():
				inx += 1
				cui_dic[cui.id] = cui.name[:10]
				if inx == 3:
					cui_dic["..."] = "..."
					break
			#print ("id sent:"+str(dish.urlname))
			fav = Picture.objects.filter(dish=dish).order_by("-likestot").first()
			if fav:
				favphoto = fav.filename()+"-med"+fav.extension()
				#print (favphoto)
			d = {'id':dish.id,'name':dish.name, 'urlname':dish.urlname, 'othernames':dish.othernames[:20], 'description':dish.description, 'cuisines':cui_dic,'favphoto':favphoto}
			data = json.dumps(d)
		else:
			data = "0"
		return HttpResponse(data, content_type="application/json")

def lookup_dish_view(request):
	#if request.is_ajax:
	if request.method == "GET":
		name = request.GET['name']
		id = request.GET['id']
		dishes = Dish.objects.none()
		if name != "":
			dishes = Dish.objects.filter(Q(name__icontains=name) | Q(othernames__icontains=name),active=True).exclude(pk=id).distinct()[:20]
		if len(dishes) > 0:
			list = []#create a list
			for row in dishes:#populate list
				inx = 0
				label = ""
				for cui in row.cuisines.all():
					inx += 1
					label += '('+cui.name+')'
					if inx == 4:
						label += "..."
						break
				if inx > 0:
					#There are cuisines in dish
					#print "There are cuisines in dish: "+row.name+" Cuisine:" +label+" |inx: "+str(inx)
					list.append({'name':row.name, 'urlname':row.urlname, 'othernames':row.othernames, 'cuisines':label})
				else:
					#No cuisines in dish
					#print "There are NO cuisines in dish: "+row.name+" |inx: "+str(inx)
					list.append({'name':row.name, 'urlname':row.urlname, 'othernames':row.othernames, 'cuisines':""})
				#list.append({'name':row.name, 'urlname':row.urlname,'othernames':row.othernames})
			#data = serializers.serialize('json', cuisines)
			#print "printing list:------------------"
			#print list
			data = json.dumps(list) #dump list as JSON
			#data = serializers.serialize('json', dishes)
		else:
			data = "0"
		return HttpResponse(data, content_type="application/json")

def lookup_othernames_view(request):
	#if request.is_ajax:
	if request.method == "GET":
		othernames = request.GET['othernames'].strip()
		if 'id' in request.GET:
			id = request.GET['id']
			dishes_all = Dish.objects.filter(active=1).exclude(id=id).order_by('name')#all active dishes
		else:
			dishes_all = Dish.objects.filter(active=1).order_by('name')#all active dishes
		dishes_similar = Dish.objects.none()
		if len(othernames)>1:
			othernames_list = [x.strip() for x in othernames.split(',')]
			othernames_list = filter(None, othernames_list)
			dishes_similar = dishes_all.filter(reduce(or_, [Q(name__icontains=c)|Q(othernames__icontains=c) for c in othernames_list])).distinct()[:20]
			if len(dishes_similar) > 0:
				list = []#create a list
				for row in dishes_similar:#populate list
					inx = 0
					label = ""
					for cui in row.cuisines.all():
						inx += 1
						label += '('+cui.name+')'
						if inx == 4:
							label += "..."
							break
					if inx > 0:
						#There are cuisines in dish
						#print "There are cuisines in dish: "+row.name+" Cuisine:" +label+" |inx: "+str(inx)
						list.append({'name':row.name, 'urlname':row.urlname, 'othernames':row.othernames, 'cuisines':label})
					else:
						#No cuisines in dish
						#print "There are NO cuisines in dish: "+row.name+" |inx: "+str(inx)
						list.append({'name':row.name, 'urlname':row.urlname, 'othernames':row.othernames, 'cuisines':""})
				data = json.dumps(list) #dump list as JSON
				#data = serializers.serialize('json', dishes_similar)
			else:
				data = "0"
			return HttpResponse(data, content_type="application/json")

def lookup_cui_view(request):
	if request.method == "GET":
		name = request.GET['name']
		id = request.GET['id']
		#print name
		cuisines = Cuisine.objects.none()
		if name != "":
			cuisines = Cuisine.objects.filter(Q(name__icontains=name) | Q(othernames__icontains=name),active=True).exclude(pk=id).distinct()
		if len(cuisines) > 0:
			data = serializers.serialize('json', cuisines)
		else:
			data = "0"
		return HttpResponse(data, content_type="application/json")

#####################################
#######   A C C O U N T    ##########
#####################################

#From myprofile.html when uploading a photo from Facebook 
@login_required(login_url=singin_url)
def profile_photo_upload_view(request):
#def dishsimilar_delete_view	(request):
	#print "user sent in URL: "+user_id
	fb_id = request.GET.get('fb_id')
	if fb_id:
		url = 'https://graph.facebook.com/'+fb_id+'/picture?width=800'
		#print "URL sent : "+url
		user_logged = request.user
		profile_logged = userProfile.objects.get(user=user_logged)
		#print "User logged: "+str(profile_logged.id)
		#print "in circle"
		from django.core.files import File
		import urllib2
		from django.core.files.temp import NamedTemporaryFile
		img_temp = NamedTemporaryFile()
		img_temp.write(urllib2.urlopen(url).read())
		img_temp.flush()
		#image = Image.open(file_path)
		#image.save(file_path)
		profile_logged.photo.save(str(profile_logged.id)+".jpg", File(img_temp))
	return HttpResponseRedirect('/myprofile/')
	
#From myprofile.html when deleting photo profile
@login_required(login_url=singin_url)
def profile_photo_delete_view(request):
	user_logged = request.user
	profile_logged = userProfile.objects.get(user=user_logged)
	#print profile_logged.photo
	filename = profile_logged.photo.path
	ruta = str(filename)
	#print "Ruta: "+ruta
	#urlname = str(photo.urlname)
	ext = str(profile_logged.extension())
	#print "Extension: "+ext
	name_only = str(profile_logged.photo).replace (ext,"").replace("users/","")
	med = settings.UPLOAD_USER+"/"+name_only+"-med"+ext
	#print "Deleling med: "+med
	if os.path.exists(ruta):
		#print "Removing: "+ruta
		os.remove(ruta)
	if os.path.exists(settings.UPLOAD_USER+"/"+name_only+"-med"+ext):
		#print "Removing: "+settings.UPLOAD_USER+"/"+name_only+"-med"+ext
		os.remove(settings.UPLOAD_USER+"/"+name_only+"-med"+ext)
	if os.path.exists(settings.UPLOAD_USER+"/"+name_only+"-thum"+ext):
		#print "Removing: "+settings.UPLOAD_USER+"/"+name_only+"-thum"+ext
		os.remove(settings.UPLOAD_USER+"/"+name_only+"-thum"+ext)
	profile_logged.photo = None
	profile_logged.save()
	return HttpResponseRedirect('/myprofile/')

#################################
#######    S I M I L A R   ######
#################################
@login_required(login_url=singin_url)
@verified_email_required
def dishsimilar_delete_view(request, dish1_id, dish2_id):
#def dishsimilar_delete_view	(request):
	#print "in Deletinh"
	user_logged = request.user
	profile_logged = userProfile.objects.get(user=user_logged)
	dish_1 = Dish.objects.get(pk=dish1_id)
	#print "Dish_1: "+dish_1.urlname
	dish_2 = Dish.objects.get(pk=dish2_id)
	#print "Dish_2: "+dish_2.urlname
	similar_obj = DishSimilar.objects.get(dish1=dish_1, dish2=dish_2, profile=profile_logged)
	#print similar_obj
	if similar_obj:
		#There is similar obj with (dishes and profile), so delete
		similar_2 = DishSimilar.objects.get(dish1=dish_2, dish2=dish_1, profile=profile_logged)
		#print "deleting:"
		similar_obj.delete()
		similar_2.delete()
	return HttpResponseRedirect('/dishsimilar/%s/'%(dish_1.urlname))

@login_required(login_url=singin_url)
@verified_email_required
def dishsimilar_view(request, urlname):
	dish = Dish.objects.get(urlname=urlname)
	similars = DishSimilar.objects.filter(dish1=dish)
	dish_sim_id_list = similars.values_list('dish2_id', flat=True)
	alert = 0
	similar = ""
	dishes = Dish.objects.filter(active=True).exclude(pk=dish.id)
	info = ""
	if request.method == "POST":
		form = similar_Form(request.POST)
		if form.is_valid():
			similar = form.cleaned_data['similar']
			similar_pk = form.cleaned_data['similar_pk']
			if similar_pk:
				#print "similar_pk:"+str(similar_pk)
				similar_new = Dish.objects.get(pk=similar_pk)
				profile = request.user
				owner = userProfile.objects.get(user=profile)
				obj, created = DishSimilar.objects.get_or_create(dish1=dish, dish2=similar_new, profile=owner, datetime=datetime.now())
				obj, created = DishSimilar.objects.get_or_create(dish1=similar_new, dish2=dish, profile=owner, datetime=datetime.now())
				return HttpResponseRedirect('/dish/%s/'%(dish.urlname))
			else:
				alert = 1
		else:
			#print "form no valid"
			print form.errors.as_text
	form = similar_Form()
	ctx = {'form':form, 'alert':alert, 'dish':dish, 'dishes':dishes, 'similars':similars,'dish_sim_id_list':dish_sim_id_list,'similar':similar}
	return render_to_response('dish_similar.html',ctx,context_instance=RequestContext(request))

############################################
####### L I K E    A C C T I O N S    ######
############################################

def photolikeaction_view(request):
	profile1 = userProfile.objects.get(pk=request.user.pk)
	liked = 0
	if request.method == "GET":
		id_photo = request.GET['photo']
		photo = Picture.objects.get(id=id_photo)
		dish = Dish.objects.get(pk=photo.dish.pk)
		obj, created = LikePicture.objects.get_or_create(profile=profile1, picture=photo, defaults={'likes': 1})
		if created:#there was not, so created one with like = 1
			#print "there was not, so created one with like = 1"
			liked = 1
			photo.like(True)
			## Update main photo in dish:
			UpdateMainPhoto(dish.pk)
			#dish.photo_main = photo.location
		else:#There is an instance,check what is it and update
			#print "There is an instance,check what is it and update"
			if obj.likes == 1:#Already liked it, so dislike
				#print "Already liked it, so dislike"
				obj.likes = 0
				photo.like(False)
				## Find out main photo:
				UpdateMainPhoto(dish.pk)
				#favphoto = Picture.objects.filter(dish=dish.pk).order_by('-likestot').first()
				#dish.photo_main = favphoto.location
				liked = 0
			else:#Already disliked it, so like it
				#print "Already disliked it, so like it"
				obj.likes = 1
				liked = 1
				photo.like(True)
				## Find out main photo:
				UpdateMainPhoto(dish.pk)
				#favphoto = Picture.objects.filter(dish=dish.pk).order_by('-likestot').first()
				#dish.photo_main = favphoto.location
		## Save dish with new main photo
		#dish.save()
		obj.save()
		data = [liked,photo.likestot]
		return HttpResponse(data)

def dishlikeaction_view(request):
	profile1 = userProfile.objects.get(pk=request.user.pk)
	liked = 0
	if request.method == "GET":
		id_dish = request.GET['dish']
		dish = Dish.objects.get(id=id_dish)
		obj, created = LikeDish.objects.get_or_create(profile=profile1, dish=dish, defaults={'likes': 1})
		if created:#there was not, so created one with like = 1
			liked = 1
			dish.like(True)
		else:
			if obj.likes == 1:
				obj.likes = 0
				liked = 0
				dish.like(False)
			else:
				obj.likes = 1
				liked = 1
				dish.like(True)
		obj.save()
		data = [liked,dish.likestot]
		return HttpResponse(data)

def listlikeaction_view(request):
	req_user = userProfile.objects.get(pk=request.user.pk)
	liked = 0
	if request.method == "GET":
		id_list = request.GET['list']
		list = List.objects.get(id=id_list)
		obj, created = LikeList.objects.get_or_create(profile=req_user, list=list)
		if created:#there was not, so created
			liked = 1
			list.like(True)
		else:#This profile already liked the dish so dishlike or delete
			obj.delete()
			liked = 0
			list.like(False)
		data = [liked,list.likestot]
		return HttpResponse(data)
		
####################################
#########   O T H E R     ##########
####################################

def contact_view(request):
	info_enviado = False # Define si se envio la informacion o no
	is_robot = False # Flag when robot defense activated
	email = ""
	titulo = ""
	text = ""
	if request.method == "POST":
		formulario = ContactForm(request.POST)
		if formulario.is_valid():
			info_enviado = True
			email = formulario.cleaned_data['Email']
			titulo = formulario.cleaned_data['Title']
			text = formulario.cleaned_data['Comment']
			robot = formulario.cleaned_data['text']
			test = formulario.cleaned_data['test']
			#print test
			if robot == "" and test == '3':
				#print "Empty"
				#print robot
				is_robot = False
				# Secret field empty, and dropdown test passed, this is a person, submit
				# Configuracion enviando mensaje via Gmail
				to_admin = 'itisclaudio@gmail.com'
				html_content = "Comments from World Food Guide Website<br> From email: [%s]<br><br>***Mensaje***<br><br>%s"%(email,text)
				msg = EmailMultiAlternatives('WorldFood.Guide - Contact',html_content,'from@server.com',[to_admin])
				msg.attach_alternative(html_content,'text/html') #Definimos el contenido como HTML
				msg.send() # Enviamos correo
			else:
				#print "not empty"
				#print robot
				# Secret field filled, and dropdown test failed, this is a Robot, don't submit
				is_robot = True
				info_enviado = False
				# Configuracion enviando mensaje via Gmail
				#to_admin = 'itisclaudio@gmail.com'
				#html_content = "Robot comments blocked<br> From email: [%s]<br><br>***Mensaje***<br><br>%s"%(email,text)
				#msg = EmailMultiAlternatives('WorldFood.Guide - Contact',html_content,'from@server.com',[to_admin])
				#msg.attach_alternative(html_content,'text/html') #Definimos el contenido como HTML
				#msg.send() # Enviamos correo
	else:
		formulario = ContactForm()
	ctx = {'form':formulario,'email':email,'titulo':titulo,'texto':text,'info_enviado':info_enviado,'is_robot':is_robot}
	return render_to_response('contact.html',ctx,context_instance=RequestContext(request))

def siteindex_view(request):
    return render_to_response('siteindex.html',context_instance=RequestContext(request))

def about_view(request):
    mensaje = "Esto es un mensaje desde mi vista"
    cxt = {'msg':mensaje}
    return render_to_response('about.html',cxt,context_instance=RequestContext(request))

def help_view(request):
    return render_to_response('help.html',context_instance=RequestContext(request))

def guidelines_view(request):
    return render_to_response('guidelines.html',context_instance=RequestContext(request))

def terms_view(request):
    return render_to_response('terms.html',context_instance=RequestContext(request))
	
############################
####    A C C E S S     ####
############################

def signin_view(request, mensa=None):
	# mensa = 1: There is no password, only social account.
	# can be sent from passrecovery_view and login
	ctx = {'mensa':mensa}
	return render_to_response('signin.html',ctx,context_instance=RequestContext(request))

def login_view(request, mensa=None):
	#mensa = "mensa"
	next = ""
	user_sent = ""
	user = User.objects.none()
	if request.user.is_authenticated():
		#return HttpResponseRedirect('/myprofile/')
		return redirect('view_myprofile')
	else:
		if request.GET:
			#next = request.GET['next']
			next = request.GET.get('next',False)
			#next = request.POST.get('name', False);
		if request.method == "POST":
			form = LoginForm(request.POST)
			if form.is_valid():
				#print "Form Valid"
				username_form = form.cleaned_data['username']
				password = form.cleaned_data['password']
				try:
					user = User.objects.get(username=username_form)
					profile = userProfile.objects.get(user=user)
					if profile.only_social == True: #user only have a social password
						#print "User has only a social account"
						mensa = 2 #social account, no password with WFG
						return redirect('view_signin', mensa = mensa)
					#There is a user with this username
					else:
						#try to login
						usuario = authenticate(username=username_form,password=password)
						#print "autenticated!"
						if usuario is not None and usuario.is_active:
							login(request,usuario)
							#print "Loged in"
							if next =="":
								return redirect('view_myprofile')
							else:
								return HttpResponseRedirect(next)
						else:
							mensa = 1 #Username exists but it is inactive
				except User.DoesNotExist:
					mensa = 4 #Username doesn't exist
					#user = None
					ctx = {'form':form,'mensa':mensa,'next':next,'user_req':username_form}
					return render_to_response('login.html',ctx,context_instance=RequestContext(request))
			else:
				#ctx = {'information':mensa, 'form':form }
				ctx = {'form':form,'mensa':mensa,'next':next,'user_req':user}
				return render_to_response('login.html',ctx,context_instance=RequestContext(request))
		form = LoginForm(initial={'username':user_sent})
		ctx = {'form':form,'mensa':mensa,'next':next,'user_req':user}
		return render_to_response('login.html',ctx,context_instance=RequestContext(request))


## When account was created using social media plugin "allauth" and now wants to create a WFG password
@login_required(login_url=singin_url)
def create_pass_view(request):
	mensa = 1
	provider = "wfg"
	req_user = request.user
	profile = userProfile.objects.get(user=req_user)
	if profile.only_social == False: #User has a WFG password
		#print "profile.only_social == False:"
		#return HttpResponseRedirect('/myprofile/')
		return redirect('view_myprofile')
	so = SocialAccount.objects.filter(user=req_user)
	if request.method == "POST":
		form = UpdatePasswordForm(request.POST, instance=req_user)
		if form.is_valid():
			pass1 = form.cleaned_data['password']
			#profile = userProfile.objects.get(user=req_user)
			#userProf = userProfile(id=user.id)
			req_user.set_password(pass1)
			profile.pass_backup = pass1
			profile.only_social = False
			form.save()
			profile.save()
			usuario = authenticate(username=req_user.username,password=pass1)
			login(request,usuario)
			#print "Loged in"
			#return HttpResponseRedirect('/myprofile/')
			return redirect('view_myprofile')
		else:
			ctx = {'information':mensa, 'form':form }
			return render_to_response('update_password_social.html',ctx,context_instance=RequestContext(request))
	form = UpdatePasswordForm(instance=req_user)
	ctx = {'form':form, 'user':req_user, 'information':mensa}
	return render_to_response('update_password_social.html',ctx,context_instance=RequestContext(request))

def signup_view(request):
	if request.user.is_authenticated():
		logout(request)
	is_robot = False # Flag when robot defense activated
	if request.method == "POST":
		form = SignupForm(request.POST, request.FILES)
		if form.is_valid():
			fname = form.cleaned_data['first_name'].lstrip().rstrip()
			lname = form.cleaned_data['last_name'].lstrip().rstrip()
			pass1 = form.cleaned_data['password'].lstrip().rstrip()
			pass2 = form.cleaned_data['password'].lstrip().rstrip()
			emailNew = form.cleaned_data['email'].lstrip().rstrip()
			username1 = form.cleaned_data['username'].lstrip().rstrip()
			about = form.cleaned_data['about']
			names_show = form.cleaned_data['names_show']
			email_show = form.cleaned_data['email_show']
			photo = form.cleaned_data['photo']
			test = form.cleaned_data['test']
			#print test
			if test == '3':
				#Answered right the question
				#May not be a robot
				is_robot = False
				user = User()
				user.username=username1
				user.email=emailNew
				user.last_name = lname
				user.first_name = fname
				user.set_password(pass1)
				user.save()
				userProf = userProfile(id=user.id)
				userProf.user_id = user.id
				userProf.pass_backup = pass1
				userProf.photo = photo
				userProf.telefono = ""
				userProf.about = about
				userProf.names_show = names_show
				userProf.email_show = email_show
				userProf.only_social = False
				userProf.uploads = 0
				userProf.save()
				#obj, created = EmailAddress.objects.get_or_create(user=user, email=emailNew, defaults={'verified': False,'primary':True})
				obj, created = EmailAddress.objects.get_or_create(user=user, email=emailNew)
				obj.save()
				email_url=request.build_absolute_uri('/')+'foodie/%s/'%(username1)
				SaveEmailQueue(user.username,'Foodie','Added',email_url)
				return HttpResponseRedirect('/login/')
			else:
				#print robot
				is_robot = True
				info_enviado = False
				# Configuracion enviando mensaje via Gmail
				to_admin = 'itisclaudio@gmail.com'
				html_content = "Robot signup blocked<br><br>From email: %s<br>Username: %s"%(emailNew,username1)
				msg = EmailMultiAlternatives('WorldFood.Guide - Signup',html_content,'from@server.com',[to_admin])
				msg.attach_alternative(html_content,'text/html') #Definimos el contenido como HTML
				msg.send() # Enviamos correo
		else:
			#form = SignupForm(initial={'names_show':names_show,'email_show':email_show})
			ctx = {'form':form, 'is_robot':is_robot}
			return render_to_response('signup.html',ctx,context_instance=RequestContext(request))
	form = SignupForm()
	ctx = {'form':form, 'is_robot':is_robot}
	return render_to_response('signup.html',ctx,context_instance=RequestContext(request))

def passrecovery_view(request):
	mensaje ="" #1(done, create boton log in), 2(email no exsite, sign up),0(From empty)
	if request.user.is_authenticated():
		logout(request)
	if request.method == "POST":
		form = PassRecovForm(request.POST)
		if form.is_valid():
			emailNew = form.cleaned_data['email']
			ux = User.objects.filter(is_active=1)
			if ux.filter(email=emailNew).exists():#Existe usuario con ese email
				u = User.objects.get(email=emailNew)
				us = userProfile.objects.get(pk=u.id)
				passw = us.pass_backup
				if passw != "": # User created a password, send email
					emailMess = "Your username is: "+str(u.username)+" and your password is: "+str(passw)
					msg = EmailMultiAlternatives('WorldFood.Guide - Password Recovery',emailMess,'donotreply@WorldFood.guide',[emailNew])
					msg.attach_alternative(emailMess,'text/html') #Definimos el contenido como HTML
					msg.send() # Enviamos correo
					mensaje = 1
					ctx = {'form':form, 'mensa':mensaje, 'user':u, 'userPro':us, 'pass':passw, 'email':emailNew}
					#return HttpResponseRedirect('/login/%s/'%(dish.urlname))
					return login_view(request,3)
					#return render_to_response('passrecovery.html',ctx,context_instance=RequestContext(request))
				else:# User didn't create a password. Used social media to sign up
					mensa = 2
					# Redirect to login with mensa = 2 "No pass, only social account"
					return redirect('view_signin', mensa = mensa)
			mensaje = 2
			ctx = {'form':form, 'mensa':mensaje, 'email':emailNew}
			return render_to_response('passrecovery.html',ctx,context_instance=RequestContext(request))
		else:
			ctx = {'form':form}
			return render_to_response('passrecovery.html',ctx,context_instance=RequestContext(request))
	form = PassRecovForm()
	mensaje = 0
	ctx = {'form':form, 'mensa':mensaje}
	return render_to_response('passrecovery.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
def myprofile_view(request):
	mensa = 1
	provider = "wfg"
	user1 = request.user
	profile = userProfile.objects.get(user=user1)
	so = SocialAccount.objects.filter(user=user1)
	ctx = {}
	if so:
		social_account = SocialAccount.objects.get(user=user1)
		#print social_account
		provider = social_account.provider
		ctx = {'user':user1,'profile':profile, 'information':mensa,'social':social_account,'provider':provider}
	else:
		ctx = {'user':user1,'profile':profile, 'information':mensa,'social':'none','provider':provider}
	return render_to_response('myprofile.html',ctx,context_instance=RequestContext(request))

#Templeate: myprofile, when user wants to unlink its social account from WFG
@login_required(login_url=singin_url)
def unlink_account_view(request):
	user = request.user
	#print "user requested: "+str(user)
	so = SocialAccount.objects.filter(user=user)
	if so:#Consistency that check social account existence
		#there is a social account
		profile = userProfile.objects.get(user=user)
		social_account = SocialAccount.objects.get(user=user)
		#print "deleting: "+str(social_account)
		social_account.delete()
		profile.only_social = False
		profile.save()
		email = EmailAddress.objects.filter(user=user)
		#if email:#Consistency that check emial existence
			#account_email = EmailAddress.objects.get(user=user)
			#print "deleting: "+str(account_email)
			#email.delete()
	return myprofile_view(request)

def foodies_view(request, page=None):
	"""list = userProfile.objects.annotate(q_pics=Count('picture', distinct = True)).extra(
		select={
			'q_likes': 'select count(files_likepicture.likes) FROM files_likepicture, files_picture WHERE files_likepicture.picture_id = files_picture.id AND files_picture.owner_id = files_userprofile.id',
			},
	).order_by('-q_pics')"""
	##using python to sort since Django can't order_by "property or method"
	#.select_related('list','dish','owner','owner__user').prefetch_related('dish__cuisines').order_by('index')
	#foofies_top = userProfile.objects.annotate(Count('picture')).annotate(Count('list')).select_related('user').distinct().order_by('-picture__count')[:5]
	list = userProfile.objects.all().annotate(Count('picture')).annotate(Count('list')).select_related('user').distinct().order_by('-picture__count')
	#list = sorted(userProfile.objects.all().select_related('user').annotate(Count('picture')).annotate(Count('list')), key=lambda a: a.photolikes() ,reverse=True)
	#list = sorted(userProfile.objects.all(), key=lambda a: a.photolikes() ,reverse=True)
	paginator = Paginator(list,20) # 10 number of elements by page
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'paginatorlist':paginatorlist}
	return render_to_response('foodies.html',cxt,context_instance=RequestContext(request))

def userphotos_view(request,username,page=None):
	user = User.objects.get(username=username)
	#profile = userProfile.objects.get(pk=user1.pk)
	#profile = User.objects.get(username=username)
	#list_all = Picture.objects.filter(owner=user.id).order_by('dish')
	list_all = Picture.objects.filter(owner=user.id).select_related('dish','owner','owner__user').prefetch_related('dish__cuisines').order_by('dish')
	paginator = Paginator(list_all,20)
	try:
		page = int(page)
	except:
		page = 1
	try:
		paginatorlist = paginator.page(page)
	except (EmptyPage, InvalidPage):
		paginatorlist = paginator.page(paginator.num_pages)
	cxt = {'list':paginatorlist,'profile':user,'temp':list_all,}
	return render_to_response('userphotos.html',cxt,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
def privacy_view(request):
	req_user = request.user
	profile = userProfile.objects.get(user=req_user)
	#print "Starting"
	if request.method == "POST":
		#form = PrivacyForm(request.POST, instance=profile)
		form = PrivacyForm(request.POST)
		if form.is_valid():
			#form.save()
			names = form.cleaned_data['names_show']
			email = form.cleaned_data['email_show']
			#print "names: "+ str(names)
			#print "email: "+ str(email)
			profile.names_show = names
			profile.email_show = email
			profile.save()
			return HttpResponseRedirect('/myprofile/')
		else:
			#print "Form not valid"
			ctx = {'form':form, 'user':req_user}
			return render_to_response('privacy.html',ctx,context_instance=RequestContext(request))
	#form = PrivacyForm(instance=profile)
	form = PrivacyForm(initial={'names_show':profile.names_show,'email_show':profile.email_show,})
	ctx = {'form':form, 'user':req_user}
	return render_to_response('privacy.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
def updatePicture_view(request):
	mensa = 1
	req_user = request.user
	profile = userProfile.objects.get(user=req_user)
	social_account = SocialAccount.objects.none()
	so = SocialAccount.objects.filter(user=req_user)
	if so:
		social_account = SocialAccount.objects.get(user=req_user)
	#print social_account
	if request.method == "POST":
		form = PicureProfileForm(request.POST, request.FILES)
		if form.is_valid():
			photo1 = form.cleaned_data['photo']
			profile.photo = photo1
			profile.save()
			if not settings.LOCAL_DEV:
				##Change location from users_original to users
				print "profile.photo: ".format(profile.photo)
				loc = str(profile.photo)
				profile.photo = loc.replace("users_original/", "users/")
				profile.save()
			return HttpResponseRedirect('/myprofile/')
		else:
			ctx = {'form':form}
			return render_to_response('picture_profile.html',ctx,context_instance=RequestContext(request))
	form = PicureProfileForm()
	ctx = {'form':form, 'user':req_user,'profile':profile, 'information':mensa, 'social':social_account}
	return render_to_response('picture_profile.html',ctx,context_instance=RequestContext(request))

"""
	dishes = Dish.objects.filter(id__range=(4001, 5000)).order_by('id')
	updates = ()
	for dish in dishes:
		favphoto = Picture.objects.filter(dish=dish.id).order_by('-likestot').first()
		if favphoto:
			## There is a photo, use obj
			dish.photo_main = str(favphoto.location)
			print dish.photo_main
			#updates = updates + ("["+str(dish.id)+"] "+str(dish.photo_main),)
			#email_url = request.build_absolute_uri('/')+'cuisine/%s/'%(urlname)
			updates = updates + ('[%i] %s = %s ' %(dish.id, dish.name, dish.photo_main),)
			dish.save()
"""

@login_required(login_url=singin_url)
def updateAboutme_view(request):

	mensa = 1
	user = request.user
	profile = userProfile.objects.get(user=user)
	if request.method == "POST":
		form = UpdateAboutmeForm(request.POST, instance=profile)
		if form.is_valid():
			about = form.cleaned_data['about']
			profile.about = about
			profile.save()
			return HttpResponseRedirect('/myprofile/')
		else:
			ctx = {'form':form}
			return render_to_response('update_aboutme.html',ctx,context_instance=RequestContext(request))
	form = UpdateAboutmeForm(instance=profile)
	#ctx = {'form':form, 'user':user,'profile':profile, 'information':mensa, 'updates':updates}
	ctx = {'form':form, 'user':user,'profile':profile, 'information':mensa}
	return render_to_response('update_aboutme.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
def updateProfile_view(request):
	user = request.user
	profile = userProfile.objects.get(user=user)
	if request.method == "POST":
		form = UpdateUserForm(request.POST, instance=user)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/myprofile/')
		else:
			#print "form not valid"
			ctx = {'formUser':form}
			return render_to_response('update_profile.html',ctx,context_instance=RequestContext(request))
	form = UpdateUserForm(instance=user)
	ctx = {'formUser':form, 'user':user, 'profile':profile}
	return render_to_response('update_profile.html',ctx,context_instance=RequestContext(request))

@login_required(login_url=singin_url)
def updateEmail_view(request):
	user = request.user
	if request.method == "POST":
		original_emial = user.email
		form = UpdateEmailForm(request.POST, instance=user)
		if form.is_valid():	
			new_email = form.cleaned_data['email']
			form.save()
			#print "Looking for user with original emial: "+str(original_emial)
			#### START: Allauth app #####
			email = EmailAddress.objects.filter(user=user, email=original_emial)
			#print str(email)
			## Think about doing this update on model level when a user email is updated
			if email:#Consistency that check emial existence
				account_email = EmailAddress.objects.get(user=user, email=original_emial)
				if account_email:
					#print "Old email: "+str(account_email.email)
					account_email.email = new_email
					account_email.save()
					#print "New email: "+str(account_email.email)
			else:
				print "There is no email"
			#### END: Allauth app #####
			return HttpResponseRedirect('/myprofile/')
			#return render_to_response('myprofile.html',ctx,context_instance=RequestContext(request))
		else:
			ctx = {'form':form }
			return render_to_response('update_email.html',ctx,context_instance=RequestContext(request))
	form = UpdateEmailForm(instance=user)
	ctx = {'form':form, 'user':user}
	return render_to_response('update_email.html',ctx,context_instance=RequestContext(request))

	user = request.user
	#print "user requested: "+str(user)
	so = SocialAccount.objects.filter(user=user)
	if so:#Consistency that check social account existence
		#there is a social account
		profile = userProfile.objects.get(user=user)
		social_account = SocialAccount.objects.get(user=user)
		#print "deleting: "+str(social_account)
		social_account.delete()
		profile.only_social = False
		profile.save()
		email = EmailAddress.objects.filter(user=user)
		if email:#Consistency that check emial existence
			#account_email = EmailAddress.objects.get(user=user)
			#print "deleting: "+str(account_email)
			email.delete()
	return myprofile_view(request)
	
	
@login_required(login_url=singin_url)
def updatePassword_view(request):
    mensa = 1
    if request.user.is_authenticated():#Esta logeado
        mensa = 2
        req_user = request.user
        if request.method == "POST":
            form = UpdatePasswordForm(request.POST, instance=req_user)
            if form.is_valid():
                pass1 = form.cleaned_data['password']
                profile = userProfile.objects.get(user=req_user)
                #userProf = userProfile(id=user.id)
                req_user.set_password(pass1)
                profile.pass_backup = pass1
                form.save()
                profile.save()
                mensa = "New Password saved!"
                #form1 = LoginForm()
                ctx = {'information':mensa}
                logout(request)
                #return HttpResponseRedirect('/cuisine/%s/%s'%(t.cuisine.id,t.id))
                return HttpResponseRedirect('/login/')
                #return redirect('login_view')
                #return render_to_response('main/login.html', ctx,context_instance=RequestContext(request))
            else:
                mensa = 3
                ctx = {'information':mensa, 'form':form }
                return render_to_response('update_password.html',ctx,context_instance=RequestContext(request))
        form = UpdatePasswordForm(instance=req_user)
        ctx = {'form':form, 'user':req_user, 'information':mensa}
        return render_to_response('update_password.html',ctx,context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def profile_redirect_view(request,id):
	user1 = User.objects.get(pk=id)
	return profile_view(request,user1.username)

def profile_view(request, username):
	# 1 = Personal:Publicaly available.Only I can add edit
	# 2 = Public: Anybody can edit
	# 3 = Private: Only I can see it
	user1 = User.objects.get(username=username)
	profile = userProfile.objects.get(user=user1)
	likes = LikePicture.objects.filter(picture__owner=profile, likes=1).count()
	listspublic_count = List.objects.filter(owner=profile, type='2').count()
	listsprivate_count = List.objects.filter(owner=profile, type='3').count()
	listspersonal_count = List.objects.filter(owner=profile, type='1').count()
	ctx = {'profile':profile,'likes':likes,'listspublic_count':listspublic_count,'listsprivate_count':listsprivate_count,'listspersonal_count':listspersonal_count}
	return render_to_response('foodie.html',ctx,context_instance=RequestContext(request))

# Error Handlers - Start
def myerror500(request):
	#print '*'*30
	patherror = request.path
	template = loader.get_template('500c.html')
	ctx = Context({'patherror':patherror})
	return HttpResponse(content=template.render(ctx), content_type='text/html; charset=utf-8', status=500)

def myerror404(request):
	template = loader.get_template('404c.html')
	ctx = Context({'patherror':request.path})
	return HttpResponse(content=template.render(ctx), content_type='text/html; charset=utf-8', status=404)

def myerror403(request):
	template = loader.get_template('403c.html')
	ctx = Context({'patherror':request.path})
	return HttpResponse(content=template.render(ctx), content_type='text/html; charset=utf-8', status=403)

def myerror400(request):
	template = loader.get_template('400.html')
	ctx = Context({'patherror':request.path})
	return HttpResponse(content=template.render(ctx), content_type='text/html; charset=utf-8', status=400)

# Error Handlers - END