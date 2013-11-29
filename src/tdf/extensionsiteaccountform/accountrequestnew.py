import re

from five import grok
from plone.directives import form
from zope.interface import Interface
from zope.interface import Invalid
from zope import schema
from z3c.form import field, button, validator
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from tdf.extensionsiteaccountform import _

from zope.schema.interfaces import Bool

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form.browser.radio import RadioFieldWidget

from zope.component import getMultiAdapter
from Acquisition import aq_inner

from collective.z3cform.norobots.widget import NorobotsFieldWidget
from collective.z3cform.norobots.validator import NorobotsValidator


checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match

def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True



MESSAGE_TEMPLATE = """\

Account Request from %(firstname)s %(name)s <%(emailAddress)s>

Firstname: %(firstname)s
Name: %(name)s
Email: %(emailAddress)s
Preferred Username: %(preferredusername)s



%(message)s
"""



class IExtensionsiteaccountForm2(Interface):
    """Define the fields of our form
    """



    explanation=schema.Text(
        title=_(u"Important Information:"),
        description=_(u"You do not need an account to download extensions from http://extensions.libreoffice.org!"),
        readonly=True,
        required=False,
        )


    requestofaccount= schema.Text(
        title =_(u"Hosting your Extension on the LibreOffice Extensions Site: http://extensions.libreoffice.org"),
        description=_(u"Submit the form below in case you created a LibreOffice extension and want to publish it at the LibreOffice Extensions Site."),
        readonly=True,
        required=False,
        )

    infofirstextensionuploadtiming = schema.Text(
        title =_(u"Please upload your extension after you have received the credentials. Projects without files will be deleted after two weeks without further notice!"),
        readonly=True,
        required=False,
    )


    name = schema.TextLine(
        title=_(u"Lastname"),
        )


    firstname = schema.TextLine(
        title=_(u"Firstname"),
        )

    preferredusername = schema.ASCIILine(
        title=_(u"User Name (5 - 15 ASCII characters)"),
        description=_(u"Please suggest your desired username. In case your preferred username is already taken, we will add numbers to your suggestion."),
        min_length=5,
        max_length=15,
        required=False,
        )



    emailAddress = schema.ASCIILine(
        title=_(u"Your Email Address (required)"),
        constraint=validateEmail
    )

    form.mode(leaveblank='hidden')
    leaveblank = schema.ASCIILine(
        title=_(u'Please leave empty'),
        required=False,
    )


    message = schema.Text(
        title=_(u"Short Description of Your Extension Project"),
        description=_(u"Please keep between 50 to 1,000 characters"),
        min_length=50,
        max_length=1000,
        required=True,

        )

    form.widget(norobots=NorobotsFieldWidget)
    norobots = schema.TextLine(title=_(u'Are you a human ?'),
                               description=_(u'In order to avoid spam, please answer the question below.'),
                               required=True)

validator.WidgetValidatorDiscriminators(NorobotsValidator, field=IExtensionsiteaccountForm2['norobots'])
grok.global_adapter(NorobotsValidator)

class ExtensionsiteaccountForm2(form.SchemaForm):


    grok.context(ISiteRoot)
    grok.name('hosting-your-extension')
    grok.require('zope2.View')

    schema = IExtensionsiteaccountForm2

    label = _(u"Hosting your Extension(s)")
    description = _(u"Please leave a short description of your template project below.")

    ignoreContext = True


    # Hide the editable border and tabs
    def update(self):
        self.request.set('disable_border', True)
        return super(ExtensionsiteaccountForm2, self).update()

    @button.buttonAndHandler(_(u"Send"))
    def sendMail(self, action):
        """Send the email to the site administrator and redirect to the
        front page, showing a status message to say the message was received.
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage


        elif 'leaveblank' in data and data['leaveblank']:

            urltool = getToolByName(self.context, 'portal_url')

            portal = urltool.getPortalObject()

            self.request.response.redirect(portal.absolute_url())
            return

        mailhost = getToolByName(self.context, 'MailHost')
        urltool = getToolByName(self.context, 'portal_url')

        portal = urltool.getPortalObject()

        # Construct and send a message
        toAddress = portal.getProperty('email_from_address')
        source = "%s <%s>" % ('Asking for an Account on the extensions site', 'extensions@otrs.documentfoundation.org')
        subject = "%s %s" % (data['firstname'], data['name'])
        message = MESSAGE_TEMPLATE % data

        mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject, charset='utf8')

        # Issue a status message
        confirm = _(u"Thank you! Your request for an account has been received and we will create an account. You will get an email with a link to activate your account and reset the password.")
        IStatusMessage(self.request).add(confirm, type='info')

            # Redirect to the portal front page. Return an empty string as the
            # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return ''

    @button.buttonAndHandler(_(u"Cancel"))
    def cancelForm(self, action):

        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()

        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return u''


