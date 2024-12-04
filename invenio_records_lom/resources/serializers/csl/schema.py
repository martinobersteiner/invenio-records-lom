# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for CSL."""

from datetime import datetime

from marshmallow import Schema, fields, missing
from marshmallow_utils.fields import SanitizedUnicode


class LOMToCSLSchema(Schema):
    """Schema for conversion from LOM to CSL."""

    # required in CSL
    id_ = SanitizedUnicode(data_key="id", attribute="id")
    # NOTE: 'type' is incorrect as CSL but doesn't matter for generating citation-string
    # we don't store CSL-type, and LOM-learningresourcetypes don't map to it well...
    # however, 'type' doesn't influence generated citation-string
    # hence, just putting the default of "article" here suffices
    type_ = fields.Constant("article", data_key="type")

    # optional in CSL
    author = fields.Method("get_authors")
    DOI = fields.Method("get_doi")
    issued = fields.Method("get_issued")
    publisher = fields.Method("get_publisher")
    title = SanitizedUnicode(
        data_key="title",
        attribute="metadata.general.title.langstring.#text",
    )
    # consider these CSL-fields: URL, version

    def get_authors(self, obj: dict) -> list[dict]:
        """Get list of author-objects."""

        def get_csl_namedict(entity: dict) -> dict:
            if entity.get("given_names") and entity.get("family_name"):
                return {
                    "given": entity["given_names"],
                    "family": entity["family_name"],
                }
            return {
                # 'literal' is an escape-hatch of sorts:
                # when present, citation-string generation ignores all other fields
                # and uses 'literal' without any changes to it...
                "literal": entity.get("full_name", ""),
            }

        contributes = obj.get("metadata", {}).get("lifecycle", {}).get("contribute", [])
        author_entities = [
            entity
            for contribute in contributes
            for entity in contribute["entity"]
            if contribute["role"]["value"]["langstring"]["#text"] == "Author"
        ]
        return [get_csl_namedict(author_entity) for author_entity in author_entities]

    def get_doi(self, obj: dict) -> str:
        """Get DOI."""
        return obj.get("pids", {}).get("doi", {}).get("identifier", "")

    def get_issued(self, obj: dict) -> dict:
        """Get publication date in CSL-form."""
        datetime_str = obj.get("metadata", {}).get("lifecycle", {}).get("datetime", "")
        if not datetime_str:
            return missing

        dt = datetime.fromisoformat(datetime_str)
        # note: 'date-parts' is a list-of-lists
        #     outer list may contain a second date-list
        #     if so, it's interpreted as start-date/end-date respectively
        #     we only got one date, but it still needs to be a list-of-list
        return {"date-parts": [[dt.year, dt.month, dt.day]]}

    def get_publisher(self, obj: dict) -> str:
        """Get publisher."""
        contributes = obj.get("metadata", {}).get("lifecycle", {}).get("contribute", [])
        publisher_entities = [
            entity
            for contribute in contributes
            for entity in contribute["entity"]
            if contribute["role"]["value"]["langstring"]["#text"] == "Publisher"
        ]
        if not publisher_entities:
            return missing

        return publisher_entities[0].get("full_name", "")
