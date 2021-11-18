# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint from resources, for REST-API routes."""

from flask import Blueprint

blueprint = Blueprint("invenio_records_lom_ext", __name__)


@blueprint.record_once
def init(state):
    """Registers services."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    registry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-records-lom"]

    registry.register(ext.records_service, service_id="lom-records")
    registry.register(ext.records_service.files, service_id="lom-files")
    registry.register(ext.records_service.draft_files, service_id="lom-draft-files")


def create_records_bp(app):
    """Create records blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()


def create_record_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()


def create_draft_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()


def create_parent_record_links_bp(app):
    """Create parent record links blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()
