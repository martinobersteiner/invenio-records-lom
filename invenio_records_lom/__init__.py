# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from .ext import InvenioRecordsLOM
from .proxies import Lom, current_records_lom
from .version import __version__

__all__ = ("__version__", "InvenioRecordsLOM", "Lom", "current_records_lom")
