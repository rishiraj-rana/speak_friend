# Views related to interacting with the contact form.

from deform import Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.view import view_defaults

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message


from speak_friend.forms.contactus import make_contact_us_form
from speak_friend.views.controlpanel import ControlPanel
from speak_friend.forms.controlpanel import contact_us_email_notification_schema


# FIXME: attach appropriate permissions
@view_defaults(route_name='contact_us')
class ContactUs(object):
    def __init__(self, request):
        self.request = request
        settings = request.registry.settings
        self.subject = "Contact Us Form Submission: %s" % settings['site_name']
        self.sender = settings['site_from']
        cp = ControlPanel(request)

        current = cp.saved_sections.get(contact_us_email_notification_schema.name)
        if current and current.panel_values:
            self.recipients = current.panel_values['email_addresses']
        else:
            self.recipients = []

    def post(self):
        frm = make_contact_us_form()
        if self.request.method != "POST":
            return HTTPMethodNotAllowed()
        if 'submit' not in self.request.POST and \
           'cancel' not in self.request.POST:
            return self.get()
        try:
            controls = self.request.POST.items()
            captured = frm.validate(controls)
            self.notify(captured)
            if captured['came_from']:
                return HTTPFound(location=captured['came_from'])
            else:
                return HTTPFound(location=self.request.route_url('home'))
        except ValidationFailure as e:
            # the submitted values could not be validated
            html = e.render()
            if 'cancel' in self.request.POST and \
               e.cstruct['came_from']:
                return HTTPFound(location=e.cstruct['came_from'])

        return {
            'forms': [frm],
            'rendered_form': html,
        }

    def get(self):
        frm = make_contact_us_form()
        return {
            'forms': [frm],
            'rendered_form': frm.render({
                'came_from': self.request.referrer,
            }),
        }

    def notify(self, captured):
        if self.recipients:
            self.request.session.flash('Your message has been sent.',
                                       queue='success')
            mailer = get_mailer(self.request)
            reply_to = '%s <%s>' % (captured['contact_name'],
                                    captured['reply_email'])
            headers = {'Reply-To': reply_to}
            message = Message(subject=self.subject,
                              sender=self.sender,
                              recipients=self.recipients,
                              extra_headers=headers,
                              body=captured['message_body'])
            mailer.send(message)
        else:
            self.request.session.flash('No recipients have been configured.',
                                       queue='error')
