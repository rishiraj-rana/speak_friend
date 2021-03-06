from unittest import TestCase

from pyramid import testing

from speak_friend.tests.mocks import MockPasswordValidator
from sixfeetup.bowab.tests.mocks import MockSession
from speak_friend.tests.mocks import create_user


class SFBaseCase(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings({
            'site_name': "Test",
            'bowab.recaptcha_options': '',
            'bowab.recaptcha_private_key': 'foo',
            'bowab.recaptcha_public_key': 'foo',
        })
        self.config.include('pyramid_chameleon')
        self.config.add_route('yadis', '/xrds.xml')
        self.request = testing.DummyRequest()
        self.request.user = create_user('sfupadmin')
        self.request.db_session = MockSession()
        self.request.registry.password_validator = MockPasswordValidator()

    def tearDown(self):
        testing.tearDown()
