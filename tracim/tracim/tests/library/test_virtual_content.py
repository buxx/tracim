# -*- coding: utf-8 -*-
import transaction
from nose.tools import ok_, eq_
from sqlalchemy import and_
from sqlalchemy.orm.attributes import InstrumentedAttribute

from tracim.model import DBSession, User
from tracim.model.data import ContentRevisionRO, Workspace, ActionDescription, VirtualContent
from tracim.tests import TestStandard


class TestVirtualContent(TestStandard):

    def test_delete(self):
        self.test_create()
        content = DBSession.query(VirtualContent).filter(VirtualContent.label == 'TEST_CONTENT_1').one()
        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())

        DBSession.delete(content)
        DBSession.flush()

        eq_(2, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())
        eq_(1, DBSession.query(VirtualContent).filter(VirtualContent.label == 'TEST_CONTENT_1').count())
        eq_(1, DBSession.query(VirtualContent).filter(and_(
            VirtualContent.label == 'TEST_CONTENT_1'),
            VirtualContent.is_deleted == True
        ).count())

    def test_update(self):
        self.test_create()
        content = DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').one()
        ok_(content)
        content_id = content.content_id
        old_description = content.description
        new_description = 'TEST_CONTENT_DESCRIPTION_1_UPDATED'

        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.description == old_description).count())
        eq_(0, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.description == new_description).count())

        # Update a content create a new revision instead
        content.description = new_description
        DBSession.flush()

        eq_(2, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())
        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.description == old_description).count())
        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.description == new_description).count())

        # Retrieve the content with VirtualContent retrieve last revision instead
        eq_(1, DBSession.query(VirtualContent).filter(VirtualContent.content_id == content_id).count())

        content = DBSession.query(VirtualContent).filter(VirtualContent.content_id == content_id).one()
        eq_(new_description, content.description)

    def test_query(self):
        self.test_create()
        q = DBSession.query(VirtualContent).filter(VirtualContent.label == 'TEST_CONTENT_1')
        eq_(1, q.count())

    def test_create(self):
        eq_(0, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())
        eq_(0, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_1').count())

        user_admin = DBSession.query(User).filter(User.email == 'admin@admin.admin').one()
        workspace = Workspace(label="TEST_WORKSPACE_1")
        DBSession.add(workspace)
        DBSession.flush()
        eq_(1, DBSession.query(Workspace).filter(Workspace.label == 'TEST_WORKSPACE_1').count())

        self._create_content(
            owner=user_admin,
            workspace=workspace,
            type='page',
            label='TEST_CONTENT_1',
            description='TEST_CONTENT_DESCRIPTION_1',
            revision_type=ActionDescription.CREATION,
            content_id=101,  # TODO: pk ? REMOVE IT TO TEST ERROR IN ERROR MANAGEMENT
            is_deleted=False,  # TODO: pk ?
            is_archived=False,  # TODO: pk ?
        )

        eq_(1, DBSession.query(ContentRevisionRO).filter(ContentRevisionRO.label == 'TEST_CONTENT_1').count())

    # def test_proxy(self):
    #
    #     VirtualContent = VirtualContentWrap.get_virtual_class()
    #     ok_(isinstance(VirtualContent, ClassWrap))
    #
    #     ok_(isinstance(ContentRevisionRO.content_id, InstrumentedAttribute))
    #     ok_(isinstance(VirtualContent.content_id, InstrumentedAttribute))
    #
    #     content = VirtualContent()
    #     ok_(isinstance(content, ContentRevisionRO))

    def _create_content(self, *args, **kwargs):
        #VirtualContent = VirtualContentWrap.get_virtual_class()
        content = VirtualContent(*args, **kwargs)
        DBSession.add(content)
        DBSession.flush()
