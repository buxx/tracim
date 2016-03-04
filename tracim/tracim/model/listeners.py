# -*- coding: utf-8 -*-
from sqlalchemy import event

from tracim.lib.exception import ContentRevisionDeleteError
from tracim.model import DBSession
from tracim.model.data import ContentRevisionRO


@event.listens_for(DBSession, 'before_flush')
def prevent_content_revision_delete(session, flush_context, instances):
    for instance in session.deleted:
        if isinstance(instance, ContentRevisionRO) and instance.revision_id is not None:
            raise ContentRevisionDeleteError("ContentRevision is not deletable. You must make a new revision with" +
                                             "is_deleted set to True. Look at tracim.model.data.new_revision context " +
                                             "manager to make a new revision")
