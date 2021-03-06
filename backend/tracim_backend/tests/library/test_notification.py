# -*- coding: utf-8 -*-

from tracim_backend.lib.core.notifications import DummyNotifier
from tracim_backend.lib.core.notifications import NotifierFactory
from tracim_backend.lib.mail_notifier.notifier import EmailNotifier
from tracim_backend.models.auth import User
from tracim_backend.models.data import Content
from tracim_backend.tests import DefaultTest
from tracim_backend.tests import eq_


class TestDummyNotifier(DefaultTest):
    def test_dummy_notifier__notify_content_update(self):
        c = Content()
        notifier = DummyNotifier(self.app_config, self.session)
        notifier.notify_content_update(c)
        # INFO - D.A. - 2014-12-09 -
        # Old notification_content_update raised an exception


class TestNotifierFactory(DefaultTest):
    def test_notifier_factory_method(self):
        u = User()
        self.app_config.EMAIL__NOTIFICATION__ACTIVATED = True
        notifier = NotifierFactory.create(self.app_config, u)
        eq_(EmailNotifier, notifier.__class__)

        self.app_config.EMAIL__NOTIFICATION__ACTIVATED = False
        notifier = NotifierFactory.create(self.app_config, u)
        eq_(DummyNotifier, notifier.__class__)


class TestEmailNotifier(DefaultTest):
    # TODO - G.M - 04-03-2017 -  [emailNotif] - Restore test for email Notif
    pass
