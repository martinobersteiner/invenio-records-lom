# To upgrade, call the whole file with app-context
# e.g. via `pipenv run invenio shell /path/to/script.py` from your repo folder

"""Upgrade `SS` / `WS` `general.keyword`s to `summer semester` / `winter semester`."""

from copy import deepcopy

import click
from invenio_db import db

from invenio_records_lom.records.api import LOMDraft, LOMRecord


def execute_upgrade():
    """Unabbreviate SS, WS."""
    click.secho("Upgrade: expanding semester (from `SS`, `WS`)...", fg="green")

    def update_db_json(draft_or_record):
        old_json = draft_or_record.json
        if not old_json:
            # for drafts that were published/deleted, json is None/empty
            # for records with new-version/embargo, json is None/empty
            return

        new_json = deepcopy(old_json)
        general = new_json.get("metadata", {}).get("general", {})
        keywords = general.get("keyword", [])
        languages = general.get("language", [])
        if languages:
            language = languages[0]
            if language not in ["de", "en"]:
                language = "en"
        else:
            language = "en"

        translation_matrix = {
            "SS": {
                "de": "Sommersemester",
                "en": "summer semester",
            },
            "WS": {
                "de": "Wintersemester",
                "en": "winter semester",
            },
        }
        for keyword in keywords:
            langstring_text = keyword.get("langstring", {}).get("#text")
            langstring_lang = keyword.get("langstring", {}).get("lang")
            if langstring_lang == "x-none" and langstring_text in translation_matrix:
                translation = translation_matrix[langstring_text][language]
                keyword["langstring"]["#text"] = translation
                keyword["langstring"]["lang"] = language

        if new_json != old_json:
            draft_or_record.json = new_json
            db.session.add(draft_or_record)

    for draft in LOMDraft.model_cls.query.all():
        update_db_json(draft)

    for record in LOMRecord.model_cls.query.all():
        update_db_json(record)

    db.session.commit()
    click.secho("Upgrade: Successfully expanded semester (from `SS`, `WS`)", fg="green")
    click.secho(
        "NOTE: this only updated SQL-database, but not the opensearch-index", fg="red"
    )


if __name__ == "__main__":
    execute_upgrade()
