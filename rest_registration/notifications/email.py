from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_registration.settings import registration_settings
from rest_registration.utils import get_user_setting


def send_verification(user, params_signer, template_config, email=None):
    if email is None:
        email_field = get_user_setting('EMAIL_FIELD')
        email = getattr(user, email_field)

    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL or
                      from_email)
    context = {
        'user': user,
        'email': email,
        'verification_url':  params_signer.get_url(),
    }
    subject_template_name = template_config['subject']
    subject = render_to_string(subject_template_name, context=context).strip()
    body_template_name = template_config.get('body')
    text_body_template_name = template_config.get('text_body')
    html_body_template_name = template_config.get('html_body')
    is_html_body = template_config.get('is_html')

    if not html_body_template_name or not text_body_template_name:
        assert body_template_name
        if is_html_body:
            html_body_template_name = body_template_name
        text_body_template_name = body_template_name

    text_body = strip_tags(
        render_to_string(text_body_template_name, context=context))

    email_msg = EmailMultiAlternatives(
        subject, text_body, from_email, [email], reply_to=[reply_to_email])
    if is_html_body:
        html_body = render_to_string(html_body_template_name, context=context)
        email_msg.attach_alternative(html_body, 'text/html')

    email_msg.send()
