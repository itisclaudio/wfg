from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives #To send emails
from datetime import datetime
from dish.files.models import (
	EmailQueue,
	)

class Command(BaseCommand):
	help = 'Send emails in EmailQueue'

	def handle(self, *args, **options):
		#print "in WFG Commands send_emails"
		if EmailQueue.objects.filter(sent_flag = False).exists():
			#print "There are sent_flag"
			emails = EmailQueue.objects.filter(sent_flag = False)
			html_content = ""
			#print emails
			count = 1
			html_content+= "<b>({}) New updates</b><br><br>".format(len(emails))
			for email in emails:
				datetime_object = email.date.strftime("%b %d, %Y - %I:%M %p")
				html_content+= "%s - <b>%s %s</b> by <b>%s</b> on %s<br>%s<br><br>" % (count, email.object, email.action, email.username, datetime_object, email.url_plus)
				count += 1
				#email.sent_flag = True
				#email.save()
			to_admin = 'itisclaudio@gmail.com'
			msg = EmailMultiAlternatives('WFG Update',html_content,'from@server.com',[to_admin])
			msg.attach_alternative(html_content,'text/html') #Definimos el contenido como HTML
			msg.send() # Enviamos correo
			emails.update(sent_flag = True)