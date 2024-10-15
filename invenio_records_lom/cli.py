# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click command-line interface for LOM module."""
from __future__ import annotations

from itertools import count

from click import group, option, secho
from faker import Faker
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from .fixtures import publish_fake_record, publish_fake_record_over_celery
from .proxies import current_records_lom
from .records.models import LOMRecordMetadata
from .resources.serializers.oai.schema import LOMToOAISchema


@group()
def lom() -> None:
    """CLI-group for "invenio lom" commands."""


@lom.command("rebuild-index")
@with_appcontext
def rebuild_index() -> None:
    """Reindex all drafts, records."""
    secho("Reindexing records and drafts...", fg="green")

    rec_service = current_records_lom.records_service
    rec_service.rebuild_index(identity=system_identity)

    secho("Reindexed records!", fg="green")


@lom.command()
@with_appcontext
@option(
    "--pid",
    "-p",
    "pids_to_check",
    default=[],
    multiple=True,
    type=str,
    help="PIDs to check. If never used, check all records.",
)
def check(pids_to_check: tuple[str]) -> None:
    """Check records in SQL-database against marshmallow-schema for OAI.

    Note: this does not guarantee by itself that OAI-PMH API works correctly, since
    (1) Records in opensearch might not mirror records in SQL-database, call `invenio
        lom reindex` to remedy this.
    (2) Records that pass OAI-schema verification might still not play nicely with
        OAI-PMH harvesters
    That said, passing OAI-schema *is* a prerequisite for OAI-PMH API working correctly
    """
    json_by_pid = {}
    counter = count()  # running count to create differing unkwown pids
    for record in LOMRecordMetadata.query.all():
        json = record.json or {}
        if not json:
            continue
        pid = json.get("id") or f"unknown #{next(counter):0>2}"
        json_by_pid[pid] = json

    if not pids_to_check:
        pids_to_check = json_by_pid.keys()

    for pid in pids_to_check:
        if pid not in json_by_pid:
            secho(f"{pid}: could not find a record to this pid", fg="red")
            continue
        try:
            json = json_by_pid[pid]
            LOMToOAISchema().load(json.get("metadata", {}))
            secho(f"{pid}: Success", fg="green")
        except Exception as e:  # noqa: BLE001
            secho(f"{pid}: {e!r}", fg="red")


@lom.command()
@with_appcontext
@option(
    "--number",
    "-n",
    default=100,
    show_default=True,
    type=int,
    help="Number of records to be created.",
)
@option("--seed", "-s", default=42, type=int, help="Seed for RNG.")
@option(
    "--backend",
    "-b",
    default=False,
    type=bool,
    is_flag=True,
    help="Create in backend for large datasets",
)
def demo(number: int, seed: int, *, backend: bool) -> None:
    """Publish `number` fake LOM records to the database, for demo purposes."""
    secho(f"Creating {number} LOM demo records", fg="green")

    fake = Faker()
    Faker.seed(seed)

    for _ in range(number):
        if backend:
            publish_fake_record_over_celery(fake)
        else:
            publish_fake_record(fake)

    secho("Published fake LOM records to the database!", fg="green")


@lom.command()
@with_appcontext
def reindex() -> None:
    """Reindex all published records from SQL-database in opensearch-indices."""
    # TODO: also reindex drafts, built API-objects instead of pid-resolving them as invenio migration scripts do
    # TODO: actually, invenio has its own reindexing stuff, use that instead!
    secho("Reindexing LOM records...", fg="green")

    record_ids = [
        record.json["id"]
        for record in LOMRecordMetadata.query.all()
        if record.json and "id" in record.json
    ]

    service = current_records_lom.records_service
    indexer = service.indexer
    for record_id in record_ids:
        record_api_object = service.record_cls.pid.resolve(record_id)
        indexer.index(record_api_object)

    secho("Successfully reindexed LOM records!", fg="green")


# from invenio_search import current_search
# from invenio_search.errors import IndexAlreadyExistsError


# @lom.command("add-indices")
# @with_appcontext
# def add_indices():
#     """
#     Add LOM-indices to already initialized elasticsearch.

#     To initialize all invenio-indices for a fresh opensearch, use `invenio index init` instead.
#     """
#     click.secho("Adding LOM-indices to elasticsearch...", fg="green")

#     generator = current_search.create(
#         index_list=[
#             "lomrecords-records-record-v1.0.0",
#             "lomrecords-drafts-draft-v1.0.0",
#         ]
#     )

#     try:
#         for name, response in generator:
#             shards_acknowledged = response.get("shards_acknowledged", True)
#             if not response["acknowledged"] or not shards_acknowledged:
#                 click.secho(
#                     "Opensearch didn't acknowledge the request, returning the following response:",
#                     fg="red",
#                 )
#                 click.echo(response)
#                 continue
#             created_kind = "index" if "index" in response else "alias"
#             click.echo(f"created {created_kind} {name}")
#         click.secho("Added LOM-indices to elasticsearch.", fg="green")
#     except IndexAlreadyExistsError as exc:
#         click.secho(str(exc), fg="red")


# @lom.command("ls")
# @with_appcontext
# def pid_ls():
#     """Show entries from PersistentIdentifier-table."""
#     # pylint: disable-next=import-outside-toplevel
#     from invenio_pidstore.models import PersistentIdentifier

#     query = PersistentIdentifier.query.filter_by(pid_type="lomid").order_by("updated")

#     click.echo(str(query))

#     results = query.all()

#     def echo(message="", nl=False, **kwargs):
#         sep = "" if nl else "  "
#         message = str(message) + sep
#         click.echo(message, nl=nl, **kwargs)

#     for r in results:
#         echo(r.created.isoformat(timespec="seconds"))
#         echo(r.updated.isoformat(timespec="seconds"))
#         echo(r.id)
#         echo(r.pid_type)
#         echo(r.pid_value)
#         echo(r.status)
#         echo(r.object_uuid, nl=True)


# @lom.command()
# def test():
#     """T."""
#     click.secho("bold", bold=True)
#     click.secho("blink", blink=True)
#     click.secho("reverse", fg="green", reverse=True)
#     click.secho("underline", underline=True)
#     click.secho("dim", dim=True)
#     click.secho("all the colors", bg="cyan", fg="bright_red")
#     import time  # pylint: disable=import-outside-toplevel

#     def wait():
#         time.sleep(0.2)

#     with click.progressbar(
#         range(100),
#         label="progressing...",
#         item_show_func=str,
#         bar_template="%(label)s  %(bar)s | %(info)s",
#     ) as lst:
#         for __ in lst:
#             wait()
#     print("Printing might work too")
#     click.pause()
