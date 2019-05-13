from django import forms
from django.forms import ModelForm
#from django.forms.widgets import RadioSelect
from dish.files.models import Cuisine, Dish, Picture, userProfile, List, Feature
#from django.db.models import Value, IntegerField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, ButtonHolder, Submit, MultiField, Div, Fieldset, HTML, Button
from crispy_forms.bootstrap import StrictButton, InlineField, AppendedText #, FormActions
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from PIL import Image
import StringIO
#from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField#django-ajax-selects

#alphanumeric = RegexValidator(r'^[0-9a-zA-Z (),-]*$', message='Only alphanumeric characters and - are allowed.',code='invalid_data')
alphanumeric = RegexValidator(r"^['0-9a-zA-Z (),-.]*$", message="Only alphanumeric, apostrophe, hyphen, commas, periods and  parenthesis allowed.",code="invalid_data")

class BaseForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(BaseForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control'

class BaseModelForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(BaseModelForm, self).__init__(*args, **kwargs)
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control'
			
class searchAdvance_Form(BaseForm):
	names = forms.CharField(max_length=99, widget=forms.TextInput(attrs={'placeholder': 'Separated by commas', 'title':'If left blank, all names will be resulted'}), required=False)
	ingredients = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Separated by commas', 'title':'If left blank, all ingredients will be resulted'}), required=False)
	cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'size':'20','title':'If left blank, all cuisines will be resulted'}))

#222	
class search_Form(forms.Form):
	#search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, validators=[alphanumeric])
	search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
	source = forms.CharField(widget=forms.TextInput(),required=False)
	ingredients = forms.BooleanField(required=False, label="Search also in Ingredients", initial=True, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;'}))
	cuisine = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
	
class similar_Form(forms.Form):
	similar = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'off'}), required=True)
	similar_pk = forms.CharField(show_hidden_initial=True, widget=forms.TextInput(),required=False)
	def clean(self):
		return self.cleaned_data

########## LIST #########
class search_list_Form(forms.Form):
	search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Space separated words'}), required=False)
#111
class List_Form(forms.ModelForm):
	TYPE_LIST = (('1', "Personal: Only owner can add dishes"),('2', "Public: Users can add dishes"),('3', "Private: Only owner can see list"),)
	name 		= forms.CharField(max_length=92,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': '92 charactes max'}), required=True, validators=[alphanumeric])
	private		= forms.BooleanField(required=False, label="Private list", initial=False, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;vertical-align:middle;'}))
	type		= forms.ChoiceField(widget = forms.Select(attrs={'class': 'form-control','style':'font-size: 18px;'}),choices=TYPE_LIST, required=False)
	description = forms.CharField(max_length=9500, widget=forms.Textarea(attrs={'cols': 9, 'rows': 7, 'class': 'form-control'}),required=False)
	class Meta:
		model = List
		fields = ['name','description','private','type']

class list_new_Form(forms.Form):
	name = forms.CharField(max_length=92,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': '92 charactes max'}), required=True, validators=[alphanumeric])
	description = forms.CharField(show_hidden_initial=True, max_length=1990, widget=forms.Textarea(attrs={'cols': 10, 'rows': 5, 'class': 'form-control'}),required=False)
	private = forms.BooleanField(required=False, label="Private list", initial=False, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;vertical-align:middle;'}))
	def clean(self):
		return self.cleaned_data
		
class UserField(forms.CharField):
    def clean(self, value):
        super(UserField, self).clean(value)
        try:
            User.objects.get(username=value)
            raise forms.ValidationError("Someone is already using this Username. Please pick another one.")
        except User.DoesNotExist:
            return value

class EmailField(forms.CharField):
	def clean(self, value):
		super(EmailField, self).clean(value)
		oldUser = User.objects.filter(email=value)
		if oldUser.exists():
			raise forms.ValidationError("Someone is already using this email!. Please pick another one.")
		else:
			return value
"""
class Cuisine_Form(BaseModelForm):#Check may not be needed now
	class Meta:
		model = Cuisine
		fields = ['name', 'othernames', 'description']
"""

#111
#Used in list.html to update dish comments
class list_dish_comment_Form(forms.Form):
	id_listdish  = forms.IntegerField(required=False)
	comments  = forms.CharField(required=False)

class cuisine_Form(BaseForm):
	name = forms.CharField(show_hidden_initial=True, max_length=50,widget=forms.TextInput(attrs={'placeholder': '50 charactes max. Only alphanumeric characters and - \' are allowed','autocomplete':'off'}),required=True)
	othernames = forms.CharField(max_length=100 ,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas'}),required=False)
	territory = forms.CharField(max_length=100 ,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas'}),required=False)
	description  = forms.CharField(show_hidden_initial=True, widget=forms.Textarea(attrs={'cols': 10, 'rows': 10}),required=False)
	check = forms.IntegerField(required=False,initial=1)
	def clean(self):
		return self.cleaned_data

#111
#from django.db.models import Count
from django.core.files.images import get_image_dimensions
class photoAdd_Form(forms.Form):
	#location  = forms.ImageField(required=True, widget=forms.FileInput(attrs={'style':'height:46px;'}))
	location  = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control upload'}))
	comments = forms.CharField(show_hidden_initial=True, max_length=400, widget=forms.Textarea(attrs={'cols': 10, 'rows': 3, 'class': 'form-control'}),required=False)
	ownit = forms.BooleanField(required=False, label="I own it", initial=False, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;vertical-align:middle;margin-top: -8px;', 'class': 'form-control'}))
	creditsname = forms.CharField(show_hidden_initial=True, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Owner of the photo', 'class': 'form-control'}),required=False)
	creditsurl = forms.CharField(show_hidden_initial=True, max_length=2000, widget=forms.TextInput(attrs={'placeholder': 'Internet location of the photo', 'class': 'form-control', 'type': 'url'}),required=False)
	def clean(self):
		return self.cleaned_data
		
	def clean_location(self):
		picture = self.cleaned_data.get("location")
		#print picture
		if not picture:
			raise forms.ValidationError("No image!")
		else:
			w, h = get_image_dimensions(picture)
			if (w < 800 and h < 800):
				raise forms.ValidationError("The image is too small. Minimum 800 pixels width or high")
			else:
				return picture
				#return self.data['location']

class photoEdit_Form(BaseForm):
	comments = forms.CharField(show_hidden_initial=True, max_length=400, widget=forms.Textarea(attrs={'cols': 10, 'rows': 3}),required=False)
	ownit = forms.BooleanField(required=False, label="I own it", initial=False, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;vertical-align:middle;margin-top: -8px;'}))
	creditsname = forms.CharField(show_hidden_initial=True, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Owner of the photo'}),required=False)
	creditsurl = forms.CharField(show_hidden_initial=True, max_length=2000, widget=forms.TextInput(attrs={'placeholder': 'Internet location of the photo', 'type': 'url'}),required=False)
	def clean(self):
		return self.cleaned_data

class photoRotate_Form(forms.Form):
	rotation = forms.IntegerField(initial=0)

class photoCrop_Form(forms.Form):
	x = forms.IntegerField(initial=0,label="X")
	y = forms.IntegerField(initial=0,label="Y")
	w = forms.IntegerField(initial=0,label="width")
	h = forms.IntegerField(initial=0,label="height")
#333
class dishForm(BaseForm):
	name = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder': '50 charactes max. Only alphanumeric characters and - \' are allowed','autocomplete':'off'}),required=True, validators=[alphanumeric])
	#name_h = forms.CharField(show_hidden_initial=True, max_length=50,widget=forms.TextInput(),required=False)
	othernames = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas'}),required=False)
	#othernames_h = forms.CharField(show_hidden_initial=True, max_length=100,widget=forms.TextInput(),required=False)
	ingredients = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas'}),required=False)
	description = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'cols': 6, 'rows': 6,'placeholder': 'A brief description of the dish (not the recipe).'}) ,required=False)
	cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
	features = forms.ModelMultipleChoiceField(queryset=Feature.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
	#cuisines_h = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
	#check = forms.IntegerField(required=False,initial=1)

class dishphotoForm(forms.Form):
	name = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder': '- \' allowed. 50 charactes max.','autocomplete':'off','class': 'form-control'}),required=True, validators=[alphanumeric])
	othernames = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas','class': 'form-control'}),required=False)
	ingredients = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'placeholder': 'Separated by commas','class': 'form-control'}),required=False)
	description = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'cols': 6, 'rows': 6,'placeholder': 'A brief description of the dish (not the recipe).','class': 'form-control'}) ,required=False)
	cuisines = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}))
	features = forms.ModelMultipleChoiceField(queryset=Feature.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
	#check = forms.IntegerField(required=False,initial=1)
	dish = forms.IntegerField(required=False,initial=0)#0 if new dish, 'id' if dish selected
	location  = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control upload'}))
	comments = forms.CharField(max_length=400, widget=forms.Textarea(attrs={'cols': 10, 'rows': 3, 'class': 'form-control'}),required=False)
	ownit = forms.BooleanField(required=False, label="I own it", initial=False, widget=forms.CheckboxInput(attrs={'style':'height:20px;width:20px;vertical-align:middle;margin-top: -8px;', 'class': 'form-control'}))
	creditsname = forms.CharField(show_hidden_initial=True, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Owner of the photo', 'class': 'form-control'}),required=False)
	creditsurl = forms.CharField(show_hidden_initial=True, max_length=2000, widget=forms.TextInput(attrs={'placeholder': 'Internet location of the photo', 'class': 'form-control', 'type': 'url'}),required=False)
	def clean(self):
		return self.cleaned_data
		
	def clean_location(self):
		picture = self.cleaned_data.get("location")
		if picture:
			w, h = get_image_dimensions(picture)
			if (w < 800 and h < 800):
				raise forms.ValidationError("The image is too small. Minimum 800 pixels width or high")
			else:
				return picture
				#return self.data['location']
	#111
	def clean_creditsurl(self):
		#Validates if the fields is a valid URL, already doing it in template with JQuey
		from django.core.validators import URLValidator
		from django.core.exceptions import ValidationError
		creditsurl = self.cleaned_data.get("creditsurl").strip()
		if len(creditsurl) > 0:
			#There is data in URL, check
			url = URLValidator()
			try:
				url(creditsurl)
				#print "correct URL"
				return creditsurl
			except:
				#print "wrong URL"
				raise forms.ValidationError("Please enter a valid URL")

class LoginForm(BaseForm):
	username = forms.CharField(max_length=75, required=True, widget=forms.TextInput())
	password = forms.CharField(required=True, widget=forms.PasswordInput(render_value=False))

class SignupAllauthForm(forms.Form):
	username = UserField(max_length=30, initial="Test1")#Getting properties from: \Lib\site-packages\allauth\account\forms.py
	email = EmailField(required=True)#Getting properties from: \Lib\site-packages\allauth\account\forms.py

	def signup(self, request, user):
		#print "In signup of dish.files.forms.SignupAllauthForm"
		#Saving for user
		#print "saving user: "+user.username
		user.username = self.cleaned_data['username']
		user.save()
		#Saving for userProfile
		#print "saving userProfile:"
		#print "In form signup(), saving userProfile"
		userProf = userProfile(id=user.id)
		userProf.user_id = user.id
		userProf.pass_backup = ""
		#userProf.photo = photo
		userProf.telefono = ""
		userProf.about = ""
		userProf.names_show = True
		userProf.email_show = True
		userProf.only_social = True
		userProf.uploads = 0
		userProf.save()

class SignupForm(forms.Form):
	first_name = forms.CharField(max_length=30 ,required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	last_name = forms.CharField(max_length=30 ,required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	username = UserField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
	photo  = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control upload'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}) ,required=True, label="Repeat your password")
	email = EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	email2 = forms.EmailField(label="Repeat your email" ,required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
	about = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'cols': 6, 'rows': 6,'class': 'form-control'}) ,required=False)
	names_show = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
	#names_show = forms.ChoiceField(widget=RadioSelect(attrs={'class': 'form-control'}), choices=[(True, 'Yes'), (False, 'No')])
	email_show = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
	BOTS_TEST = (('', "--Select answer--"),('1', "Bridge, Building, House"),('2', "Window, Ceiling, Floor"),('3', "Bread, Rice, Apples"),('4', "Red, Blue, Pink"),)
	test = forms.ChoiceField(widget = forms.Select(attrs={'class': 'form-control','style':'font-size: 18px;'}), choices=BOTS_TEST)

	def clean_email(self):
		if self.data['email'] != self.data['email2']:
			raise forms.ValidationError('Emails are not the same')
		return self.data['email']

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords are not the same')
		return self.data['password']
		
	def clean_username(self):
		username1 =  self.data['username'].lstrip().rstrip()
		username1 =  username1.replace (" ", "_")
		return username1

	def clean(self,*args, **kwargs):
		self.clean_email()
		self.clean_password()
		self.clean_username()
		return super(SignupForm, self).clean(*args, **kwargs)
		
class PassRecovForm(BaseForm):
    email = forms.EmailField(required=True)
    
    def clean(self,*args, **kwargs):
        return super(PassRecovForm, self).clean(*args, **kwargs)

class PrivacyForm(BaseForm):
	names_show = forms.BooleanField(required=False)
	email_show = forms.BooleanField(required=False)
	class Meta:
		model = userProfile
		fields = ["names_show","email_show"]
	
class UpdateUserForm(BaseModelForm):
    class Meta:
        model = User
        fields = ["username","first_name","last_name"]
	
class UpdateAboutmeForm(BaseModelForm):
	about = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'cols': 6, 'rows': 16}) ,required=False)
	class Meta:
		model = userProfile
		fields = ["about"]		

class UpdateEmailForm(BaseModelForm):
	email = EmailField(required=True)
	email2 = forms.EmailField(label="Repeat your email" ,required=True)

	def clean_email(self):
		if self.data['email'] != self.data['email2']:
			raise forms.ValidationError('Emails are not the same')
		return self.data['email']

	class Meta:
		model = User
		fields = ["email"]

class UpdatePasswordForm(BaseModelForm):
	password = forms.CharField(widget=forms.PasswordInput() ,required=True,  label="New password", help_text='Max 30')
	password2 = forms.CharField(widget=forms.PasswordInput() ,required=True, label="Repeat your new password")

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords are not the same')
		return self.data['password']

	class Meta:
		model = User
		fields = ["password"]
		
class PicureProfileForm(forms.Form):
	photo  = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control upload'}))
	def clean(self):
		return self.cleaned_data
#111
class ContactForm(BaseForm):
	BOTS_TEST = (('', "--Select--"),('1', "Bridge, Building, House"),('2', "Window, Ceiling, Floor"),('3', "Bread, Rice, Apples"),('4', "Red, Blue, Pink"),)
	Email   = forms.EmailField(widget=forms.TextInput())
	Title  = forms.CharField(widget=forms.TextInput())
	Comment= forms.CharField(widget=forms.Textarea())
	text = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'display:none;'}))
	test = forms.ChoiceField(widget = forms.Select(attrs={'class': 'form-control','style':'font-size: 18px;'}),choices=BOTS_TEST, required=True)