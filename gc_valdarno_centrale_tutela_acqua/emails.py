# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string


def send_feedback_email(email, codice_segnalazione):
    c = Context({'email': email, 'codice_segnalazione': codice_segnalazione})

    email_subject = render_to_string(
        'email/feedback_email_subject.txt', c).replace('\n', '')
    email_body = render_to_string('email/feedback_email_body.txt', c)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        ['mari@lamma.rete.toscana.it'],
        headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}
    )
    return email.send(fail_silently=False)