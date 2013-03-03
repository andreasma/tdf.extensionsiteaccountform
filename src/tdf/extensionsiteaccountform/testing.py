from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class TdfextensionsiteaccountformLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import tdf.extensionsiteaccountform
        xmlconfig.file(
            'configure.zcml',
            tdf.extensionsiteaccountform,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'tdf.extensionsiteaccountform:default')

TDF_EXTENSIONSITEACCOUNTFORM_FIXTURE = TdfextensionsiteaccountformLayer()
TDF_EXTENSIONSITEACCOUNTFORM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TDF_EXTENSIONSITEACCOUNTFORM_FIXTURE,),
    name="TdfextensionsiteaccountformLayer:Integration"
)
