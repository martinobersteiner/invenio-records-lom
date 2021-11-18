# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from flask import Blueprint

from .records import init_records_views


def create_blueprint(app):
    blueprint = Blueprint(
        "invenio_records_lom",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    init_records_views(blueprint, app)

    return blueprint
