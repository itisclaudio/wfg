#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dish.settings")
django.setup()

from django.core.mail import EmailMultiAlternatives #To send emails
#from dish.files.models import EmailQueue
#from dish import models
from dish.files.models import EmailQueue
from datetime import datetime

def CheckEmails():
	print "in cron_jobs.py CheckEmails()"
	if EmailQueue.objects.filter(sent_flag = False).exists():
		emails = EmailQueue.objects.filter(sent_flag = False)
		html_content = ""
		print emails
		count = 1
		for email in emails:
			#content sample: 1 - Cuisine Added by <username> on <date>
			#str(email.date)[0:15]
			datetime_object = email.date.strftime("%b %d, %Y - %I:%M %p")
			#datetime_object = datetime.strptime(str(email.date), '%b %d %Y %I:%M%p')
			html_content+= "%s - <b>%s %s</b> by <b>%s</b> on %s<br>%s<br><br>" % (count, email.object, email.action, email.username, datetime_object, email.url_plus)
			#html_content+= "<b>%s %s</b> by %s on %s<br>%s<br><br>" % (email.object, email.action, email.username, email.date, email.url_plus)
			count += 1
			#email.sent_flag = True
			#email.save()
		to_admin = 'itisclaudio@gmail.com'
		msg = EmailMultiAlternatives('WFG Update',html_content,'from@server.com',[to_admin])
		msg.attach_alternative(html_content,'text/html') #Definimos el contenido como HTML
		msg.send() # Enviamos correo
		emails.update(sent_flag = True)
		
if __name__ == "__main__":
	print "in cron_jobs.py __NAME__:"
	CheckEmails()