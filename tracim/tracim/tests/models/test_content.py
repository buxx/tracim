# -*- coding: utf-8 -*-
from sqlalchemy.testing import eq_

from tracim.model import DBSession, User, Content
from tracim.model.data import ContentRevisionRO, Workspace, ActionDescription
from tracim.tests import TestStandard


class TestContent(TestStandard):

    def test_query(self):
        content = self.test_create()
        content.description = 'TEST_CONTENT_DESCRIPTION_1_UPDATED'
        DBSession.flush()

        DBSession.query(Content).filter(Content.id == content.id).one()
        # DBSession.query(Content).join(ContentRevisionRO).filter(Content.id == content.id)
        # TODO: La query doit: filtrer sur RO (workspace == X) mais aussi se limiter au dernier enregistrement RO ! (le plus à jour)

    def test_update(self):
        created_content = self.test_create()
        content = DBSession.query(Content).filter(Content.id == created_content.id).one()
        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())

        content.description = 'TEST_CONTENT_DESCRIPTION_1_UPDATED'
        DBSession.flush()

        eq_(2, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())
        eq_(1, DBSession.query(Content).filter(Content.id == created_content.id).count())

    def test_creates(self):
        eq_(0, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())
        eq_(0, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_1').count())

        user_admin = DBSession.query(User).filter(User.email == 'admin@admin.admin').one()
        workspace = Workspace(label="TEST_WORKSPACE_1")
        DBSession.add(workspace)
        DBSession.flush()
        eq_(1, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_1').count())

        first_content = self._create_content(
            owner=user_admin,
            workspace=workspace,
            type='page',
            label='TEST_CONTENT_1',
            description='TEST_CONTENT_DESCRIPTION_1',
            revision_type=ActionDescription.CREATION,
            is_deleted=False,  # TODO: pk ?
            is_archived=False,  # TODO: pk ?
            #file_content=None,  # TODO: pk ? (J'ai du mettre nullable=True)
        )

        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())

        content = DBSession.query(Content).filter(Content.id == first_content.id).one()
        eq_('TEST_CONTENT_1', content.label)
        eq_('TEST_CONTENT_DESCRIPTION_1', content.description)

        # Create a second content
        second_content = self._create_content(
            owner=user_admin,
            workspace=workspace,
            type='page',
            label='TEST_CONTENT_2',
            description='TEST_CONTENT_DESCRIPTION_2',
            revision_type=ActionDescription.CREATION,
            is_deleted=False,  # TODO: pk ?
            is_archived=False,  # TODO: pk ?
            #file_content=None,  # TODO: pk ? (J'ai du mettre nullable=True)
        )

        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_2').count())

        content = DBSession.query(Content).filter(Content.id == second_content.id).one()
        eq_('TEST_CONTENT_2', content.label)
        eq_('TEST_CONTENT_DESCRIPTION_2', content.description)

    def test_create(self, key='1'):
        eq_(0, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_%s' % key).count())
        eq_(0, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_%s' % key).count())

        user_admin = DBSession.query(User).filter(User.email == 'admin@admin.admin').one()
        workspace = Workspace(label="TEST_WORKSPACE_1")
        DBSession.add(workspace)
        DBSession.flush()
        eq_(1, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_%s' % key).count())

        created_content = self._create_content(
            owner=user_admin,
            workspace=workspace,
            type='page',
            label='TEST_CONTENT_%s' % key,
            description='TEST_CONTENT_DESCRIPTION_%s' % key,
            revision_type=ActionDescription.CREATION,
            is_deleted=False,  # TODO: pk ?
            is_archived=False,  # TODO: pk ?
            #file_content=None,  # TODO: pk ? (J'ai du mettre nullable=True)
        )

        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_%s' % key).count())

        content = DBSession.query(Content).filter(Content.id == created_content.id).one()
        eq_('TEST_CONTENT_%s' % key, content.label)
        eq_('TEST_CONTENT_DESCRIPTION_%s' % key, content.description)

        return created_content

    def _create_content(self, *args, **kwargs):
        content = Content(*args, **kwargs)
        DBSession.add(content)
        DBSession.flush()

        return content
