# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""User interface utilities."""
# pylint: disable=too-many-lines

from flask import Blueprint, Flask

from .records import init_records_views
from .theme import init_theme_views


def create_blueprint(app: Flask) -> Blueprint:
    """Return blueprint with registered routes."""
    blueprint = Blueprint(
        "invenio_records_lom",
        __name__,
        template_folder="../templates",
        static_folder="../static",
        url_prefix="/oer",
    )

    init_records_views(blueprint, app)
    init_theme_views(blueprint, app)

    additional_urls = {
        "/lomtest/add_pids": add_pids,
        "/lomtest/add_role": add_role,
        "/lomtest/create_draft": create_draft,
        "/lomtest/datacite_rest": datacite_rest,
        "/lomtest/doi": doi,
        "/lomtest/duplicate": duplicate,
        "/lomtest/edit": edit,
        "/lomtest/file": file,
        "/lomtest/file_by_hash": file_by_hash,
        "/lomtest/import_other": import_other,
        "/lomtest/import_resources": imp_res,
        "/lomtest/mail": mail,
        "/lomtest/moodle": moodle,
        "/lomtest/new": new,
        "/lomtest/old": old,
        "/lomtest/order": order,
        "/lomtest/poll_draft_files": poll_draft_files,
        "/lomtest/principal": principal,
        "/lomtest/publish_pids": publish_pids,
        "/lomtest/read_pid": read_pid,
        "/lomtest/register_pid": register_pid,
        "/lomtest/reindex": reindex,
        "/lomtest/resource": resource,
        "/lomtest/show": show,
        "/lomtest/store_vocabs": store_vocabs_on_setup,
        "/lomtest/test": test,
        "/lomtest/upgrade_db": upgrade_db,
        "/lomtest/upgrade_db_2": upgrade_db_2,
        "/lomtest/xsd": xsd,
    }
    for url, view_func in additional_urls.items():
        blueprint.add_url_rule(url, view_func=view_func)

    return blueprint


def old():
    """O."""
    # pylint: disable=import-outside-toplevel
    from faker import Faker
    from invenio_rdm_records.cli import create_fake_record
    from invenio_rdm_records.fixtures.tasks import (
        create_demo_record as celery_wrapped_create,
    )

    Faker.seed(42)
    data = create_fake_record()
    create_demo_record = celery_wrapped_create.__wrapped__
    try:
        create_demo_record(user_id=1, data=data)
        return "Old: Succesful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"Old: Error {e!r}"


def new():
    """N."""
    # pylint: disable=import-outside-toplevel
    from faker import Faker

    from ..fixtures.demo import publish_fake_record

    fake = Faker()
    Faker.seed(42)

    try:
        publish_fake_record(fake)
        return "New: Succesful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"New: Error {e!r}"


def edit():
    """E."""
    # pylint: disable=import-outside-toplevel
    try:
        from ..fixtures.demo import system_identity
        from ..proxies import current_records_lom

        fake_identity = system_identity

        service = current_records_lom.records_service
        draft_item = service.edit(identity=fake_identity, id_="71v0t-eyt62")
        updated_json = draft_item.to_dict()
        updated_json["metadata"]["relation"].append(
            {
                "kind": {
                    "source": "LOMv1.0",  # default is "LOMv1.0"
                    "value": "ispartof",
                },
                "resource": {
                    "identifier": [
                        {
                            "catalog": "repo-pid",
                            "entry": "placeholder-for-testing",
                        }
                    ],
                    "description": [],
                },
            }
        )
        updated_draft_item = service.update_draft(
            identity=fake_identity, id_=draft_item.id, data=updated_json
        )
        record_item = service.publish(identity=fake_identity, id_=updated_draft_item.id)
        return str(record_item.to_dict())
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"Edit: Error {e!r}"


def show():
    """S."""
    # pylint: disable=import-outside-toplevel
    from flask import render_template

    return render_template(
        "../../../../../../../documentation/test.html",
    )


# pylint: disable-next=too-many-locals
def file():
    """F."""
    # pylint: disable=import-outside-toplevel
    try:
        from io import BytesIO
        from pathlib import Path

        from faker import Faker

        from ..fixtures.demo import create_fake_data, partial, system_identity
        from ..proxies import current_records_lom

        fake = Faker()
        Faker.seed(42)

        service = current_records_lom.records_service
        df_ser = service.draft_files

        fp = Path("/home/marobr/documentation/run-instructions")

        create = partial(service.create, identity=system_identity)
        # edit = partial(service.edit, identity=system_identity)
        publish = partial(service.publish, identity=system_identity)
        update_draft = partial(service.update_draft, identity=system_identity)

        init_files = partial(df_ser.init_files, identity=system_identity)
        set_file_content = partial(df_ser.set_file_content, identity=system_identity)
        commit_file = partial(df_ser.commit_file, identity=system_identity)

        # create and adjust input_data
        data = create_fake_data(fake, resource_type="file", files_enabled=True)
        data["access"]["embargo"] = {}
        data["access"]["files"] = "public"
        data["access"]["record"] = "public"

        # create
        draft_item = create(data=data)

        # add_file
        init_files(id_=draft_item.id, data=[{"key": fp.name}])
        set_file_content(
            id_=draft_item.id, file_key=fp.name, stream=BytesIO(fp.read_bytes())
        )
        file_item = commit_file(id_=draft_item.id, file_key=fp.name)

        # update draft with "default_preview"
        draft_data = draft_item.to_dict()
        draft_data["files"]["default_preview"] = fp.name
        updated_draft_item = update_draft(id_=draft_item.id, data=draft_data)

        # assert
        updated_draft_data = updated_draft_item.to_dict()

        assert "default_preview" in updated_draft_data["files"]

        # update in the following line only needed for default_preview
        # files-changes allow immediate publishing
        published_item = publish(id_=updated_draft_item.id)

        print(file_item.to_dict())
        print(published_item.to_dict()["files"])

        return "File: Successful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"File: Error {e!r}"


# pylint: disable-next=too-many-locals
def doi():
    """D."""
    # pylint: disable=import-outside-toplevel
    try:
        from invenio_records_resources.services.uow import TaskOp, UnitOfWork

        from ..fixtures.demo import Faker, create_fake_data, partial, system_identity
        from ..proxies import current_records_lom

        service = current_records_lom.records_service
        pids_service = service.pids
        # pylint: disable-next=protected-access
        provider = pids_service.pid_manager._get_provider("doi", "datacite")
        # check current_app.config

        fake = Faker()
        Faker.seed(42)

        with UnitOfWork() as uow:
            service_kwargs = {
                "identity": system_identity,
                "uow": uow,
            }

            create = partial(service.create, **service_kwargs)
            publish = partial(service.publish, **service_kwargs)
            pids_create = partial(pids_service.create, **service_kwargs)

            def basic_flow():
                data = create_fake_data(fake=fake, resource_type="unit")
                data["pids"] = {}

                draft = create(data=data)
                assert draft["pids"] == {}

                record = publish(id_=draft.id)
                published_doi = record["pids"]["doi"]
                assert published_doi["identifier"]
                assert published_doi["provider"] == "datacite"

                pid = provider.get(pid_value=published_doi["identifier"])
                assert pid.status

            # pylint: disable-next=unused-variable
            def publish_managed():
                data = create_fake_data(fake=fake, resource_type="file")
                draft = create(data=data)
                draft = pids_create(id_=draft.id, scheme="doi")
                # pylint: disable-next=redefined-outer-name
                doi = draft["pids"]["doi"]["identifier"]
                pid = provider.get(pid_value=doi)

                record = publish(id_=draft.id)
                pid = provider.get(pid_value=doi)
                assert record, pid.status

            basic_flow()
            # publish_managed()

            # don't `uow.commit()` on purpose, might need to call registered operations by hand
            # uow.commit() also schedules `TaskOp`s
            # pylint: disable=protected-access
            task_ops = [op for op in uow._operations if isinstance(op, TaskOp)]
            uow._operations = [
                op for op in uow._operations if not isinstance(op, TaskOp)
            ]
            uow.commit()
        # leave UnitOfWork ContextManager

        for task_op in task_ops:
            # pylint: disable=protected-access
            celery_task = task_op._celery_task
            task_args = task_op._args
            task_kwargs = task_op._kwargs

            # celery_task.delay(*task_args, **task_kwargs)
            task_func = celery_task.__wrapped__
            task_func(*task_args, **task_kwargs)

        return "DOI: Succesful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"DOI: Error {e!r}"


def datacite_rest():
    """D."""
    # pylint: disable=import-outside-toplevel
    from ..fixtures.demo import system_identity
    from ..proxies import current_records_lom
    from ..resources.serializers import LOMToDataCite44Serializer

    service = current_records_lom.records_service

    pid = "mpc2x-0s595"
    draft = service.read(system_identity, pid)
    data = draft.to_dict()
    res = LOMToDataCite44Serializer().dump_one(data)

    import yaml

    class NoAliasDumper(yaml.SafeDumper):
        """NAD."""

        def ignore_aliases(self, data):
            return True

    return yaml.dump(res, Dumper=NoAliasDumper)


def order():
    """O."""
    # pylint: disable=import-outside-toplevel
    try:
        from invenio_records_resources.services.uow import UnitOfWork

        from ..fixtures.demo import Faker, create_fake_data, system_identity
        from ..proxies import current_records_lom

        service = current_records_lom.records_service

        fake = Faker()
        Faker.seed(42)

        data = create_fake_data(fake, resource_type="unit")

        with UnitOfWork() as uow:
            draft_item = service.create(identity=system_identity, data=data, uow=uow)
            print(draft_item)

            # don't `uow.commit()` on purpose, might need to call registered operations by hand
            # uow.commit() also schedules `TaskOp`s
            # pylint: disable=protected-access
            commit_ops = uow._operations
            uow._operations = []
        # leave UnitOfWork ContextManager

        # pylint: disable-next=unused-variable
        for commit_op in commit_ops:
            ...

        return "Order: Succesful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"Order: Error {e!r}"


def duplicate():  # pylint: disable=too-many-locals
    """D."""
    # pylint: disable=import-outside-toplevel
    try:
        from io import BytesIO
        from pathlib import Path

        from ..fixtures.demo import partial, system_identity
        from ..proxies import current_records_lom

        fp = Path("/home/marobr/documentation/Pipfile.lock")

        service = current_records_lom.records_service
        df_service = service.draft_files
        service_kwargs = {"identity": system_identity}

        read = partial(service.read, **service_kwargs)

        # read
        draft_item = read(id_="")
        service_kwargs["id_"] = draft_item.id

        init_files = partial(service.draft_files.init_files, **service_kwargs)
        set_file_content = partial(df_service.set_file_content, **service_kwargs)
        commit_file = partial(service.draft_files.commit_file, **service_kwargs)

        # add_file
        init_files(data=[{"key": fp.name}])
        set_file_content(file_key=fp.name, stream=BytesIO(fp.read_bytes()))
        file_item = commit_file(file_key=fp.name)

        # update draft with "default_preview"
        # ...

        print(file_item.to_dict())
        print(draft_item.to_dict()["files"])

        return "File: Successful Exit"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"File: Error {e!r}"


def mail():
    """M."""
    from flask import current_app  # pylint:disable=import-outside-toplevel
    from flask_mail import Message  # pylint:disable=import-outside-toplevel

    try:
        current_app.config["DEBUG"] = False
        current_app.config["debug"] = False
        current_app.config["MAIL_SUPPRESS_SEND"] = False
        # TODO: fill this in
        msg = Message(
            "Testing mail was succesful",
            sender="todo@here.ext",
            recipients=["obersteiner.mar@gmail.com"],
            body="hey there, future me",
        )
        mail_ext = current_app.extensions["mail"]
        mail_ext.send(msg)

        return "success"

    except Exception as exc:  # pylint: disable=broad-except
        return str(exc)

    finally:
        current_app.config["DEBUG"] = True
        current_app.config["debug"] = True
        current_app.config["MAIL_SUPPRESS_SEND"] = True


def imp_res():
    """IR."""
    # pylint: disable=import-outside-toplevel
    from ..utils.util import get_learningresourcetypedict, get_oefosdict

    get_learningresourcetypedict()

    get_oefosdict()

    return "finished"


def moodle():
    """M."""
    # pylint: disable=import-outside-toplevel
    import json
    from pathlib import Path
    from pprint import pprint

    import yaml
    from flask import current_app

    # pylint: disable-next=import-error
    from invenio_moodle.utils import insert_moodle_into_db

    config = current_app.config
    pprint(config["LOM_PERSISTENT_IDENTIFIER_PROVIDERS"])
    pprint(config["LOM_PERSISTENT_IDENTIFIERS"])

    path = Path("/home/marobr/documentation/jupyter-notebooks/moodle.json")
    moodle_data = json.loads(path.read_text(encoding="utf-8"))
    yaml_path = Path(
        "/home/marobr/documentation/jupyter-notebooks/moodle-files/paths_by_url.yaml"
    )
    with yaml_path.open(encoding="utf-8") as fh:
        paths_by_url = {url: Path(path) for url, path in yaml.safe_load(fh).items()}

    # mock new moodle-fields
    moodle_data["applicationprofile"] = "mock"
    for moodle_course in moodle_data["moodlecourses"]:
        for file_data in moodle_course["files"]:
            file_data["contenthash"] = "mock-hash"

    # call moodle-stuff
    try:
        insert_moodle_into_db(moodle_data, paths_by_url)
    except Exception as exc:  # pylint: disable=broad-except
        print(repr(exc))
        return repr(exc)
    return "Moodle: Success"


# pylint: disable-next=too-many-locals
def file_by_hash():
    """FI."""
    # pylint: disable=import-outside-toplevel
    # pylint: disable=unreachable
    import hashlib
    from functools import partial
    from io import BytesIO

    from faker import Faker
    from invenio_access.permissions import system_identity
    from invenio_files_rest.models import FileInstance

    from ..fixtures import create_fake_data
    from ..proxies import current_records_lom

    service = current_records_lom.records_service
    create = partial(service.create, identity=system_identity)
    # update_draft = partial(service.update_draft, identity=system_identity)
    df_service = service.draft_files
    commit_file = partial(df_service.commit_file, identity=system_identity)
    init_files = partial(df_service.init_files, identity=system_identity)
    set_file_content = partial(df_service.set_file_content, identity=system_identity)

    fake = Faker()
    Faker.seed(42)

    data = create_fake_data(fake, resource_type="file", files_enabled=True)
    draft_item = create(data=data)

    content = b"test"
    init_files(id_=draft_item.id, data=[{"key": "filename"}])
    set_file_content(id_=draft_item.id, file_key="filename", stream=BytesIO(content))
    commit_file(id_=draft_item.id, file_key="filename")

    hash_md5 = hashlib.md5(content).hexdigest()  # of form '098f6...'
    print(hash_md5)
    checksum = f"md5:{hash_md5}"  # of form 'md5:098f6...'
    fis = FileInstance.query.filter_by(checksum=checksum).all()
    path = fis[0].uri  # contains path to file
    print(path)

    return "Success"


# pylint: disable-next=too-many-locals
def read_pid():
    """R."""
    # pylint: disable=import-outside-toplevel
    # pylint: disable=broad-except
    from functools import partial

    from invenio_access.permissions import system_identity

    from ..proxies import current_records_lom

    service = current_records_lom.records_service
    read = partial(service.read, identity=system_identity)
    read_draft = partial(service.read_draft, identity=system_identity)

    pid = "wnta4-5r386"

    try:
        a = read(id_=pid)
        print(a)
    except Exception as e:
        print(repr(e))
    try:
        b = read_draft(id_=pid)
        print(b)
    except Exception as e:
        print(repr(e))

    from invenio_rdm_records.fixtures.demo import create_fake_record
    from invenio_rdm_records.proxies import current_rdm_records_service

    create = partial(current_rdm_records_service.create, identity=system_identity)
    read_draft = partial(
        current_rdm_records_service.read_draft, identity=system_identity
    )

    try:
        data = create_fake_record()
        data["metadata"]["creators"][0]["affiliations"] = [
            {"id": "asdfg-hjk42", "name": "test"}
        ]
        draft_item = create(data=data)
        c = read_draft(id_=draft_item.id)
        print(c)
    except Exception as e:
        print(repr(e))


def create_draft():
    """D."""
    # pylint: disable=import-outside-toplevel
    from functools import partial

    from faker import Faker
    from flask import g

    # from invenio_access.permissions import system_identity
    from ..fixtures.demo import attach_fake_files, create_fake_data
    from ..proxies import current_records_lom

    fake = Faker()
    Faker.seed(42)

    service = current_records_lom.records_service
    create = partial(service.create, identity=g.identity)

    try:
        file_data = create_fake_data(fake, resource_type="file", files_enabled=True)
        draft_item = create(data=file_data)
        attach_fake_files(fake, draft_item)

        return f"Draft: Succesfully created {draft_item.id}"
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return f"draft: Error {e!r}"


def poll_draft_files():
    """P."""
    # pylint: disable=import-outside-toplevel
    import requests

    try:
        requests.post(
            "https://127.0.0.1:5000/api/lom/8mssa-f2656/draft/files", timeout=60 * 60
        )
        return "Successfully returned"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


# pylint: disable-next=too-many-locals
def test():
    """T."""
    # do `test_create_draft`, which fails for some reason
    # pylint: disable=import-outside-toplevel
    import json as jsonlib

    from invenio_access.permissions import system_identity
    from invenio_db import db
    from invenio_pidstore.models import PersistentIdentifier

    from ..proxies import current_records_lom
    from ..records.models import LOMDraftMetadata, LOMParentMetadata, LOMVersionsState

    service = current_records_lom.records_service

    def _get_session_commits():
        """Get objects that have already been commited in this session."""
        return set(db.session.identity_map.values())

    def _pick_by_cls(iterable, cls, assert_unique=True):
        """Get first obj from `iterable` whose class is `cls`."""
        instances = [obj for obj in iterable if isinstance(obj, cls)]
        if assert_unique:
            assert len(instances) == 1
        return instances[0]

    try:
        title_langstring = {"langstring": {"#text": "Test", "lang": "en"}}
        access = {"files": "public", "record": "public", "embargo": {}}
        data = {
            "access": access,
            "files": {"enabled": False},
            "metadata": {"general": {"title": title_langstring}},
            "resource_type": "course",
        }

        db_before = _get_session_commits()
        service.create(identity=system_identity, data=data)
        db_after = _get_session_commits()
        db_new_values = db_after - db_before

        new_parent = _pick_by_cls(db_new_values, LOMParentMetadata)
        new_draft = _pick_by_cls(db_new_values, LOMDraftMetadata)
        new_versions_state = _pick_by_cls(db_new_values, LOMVersionsState)

        new_pids = [o for o in db_new_values if isinstance(o, PersistentIdentifier)]
        assert len(new_pids) == 2
        parent_pid = next(pid for pid in new_pids if pid.object_uuid == new_parent.id)
        draft_pid = next(pid for pid in new_pids if pid.object_uuid == new_draft.id)

        assert parent_pid.status.value == "N"
        assert draft_pid.status.value == "N"
        assert new_versions_state.next_draft_id == new_draft.id
        assert new_versions_state.parent_id == new_parent.id
        assert new_draft.parent_id == new_parent.id

        new_json = new_draft.json
        assert "metadata" in new_json
        assert "general" in new_json["metadata"]
        general = new_json["metadata"]["general"]
        json_pid = (
            general.get("identifier", {})[0]
            .get("entry", {})
            .get("langstring", {})
            .get("#text", "")
        )
        assert json_pid == draft_pid.pid_value

        del general["identifier"]

        return f"""<div style="white-space: pre; font-family: monospace">
  {jsonlib.dumps({"draft": new_json['metadata'], "original": data['metadata'], 'pid': draft_pid.pid_value,'same': new_json['metadata'] == data['metadata']}, indent=2)}
</div>"""
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def resource():
    """R."""
    # pylint: disable=import-outside-toplevel
    from ..resources import LOMRecordResource

    return f"""{repr(dir(LOMRecordResource))}</br>
        {repr(LOMRecordResource.decorators)}</br>
        {repr(dir(LOMRecordResource.decorators[0]))}</br>
        {repr(LOMRecordResource.decorators[0].__closure__)}"""


def register_pid():
    """R."""
    # pylint: disable=import-outside-toplevel

    from ..services.tasks import register_or_update_pid as register_task

    register = register_task.__wrapped__

    try:
        register(recid="gbh6r-p5r09", scheme="doi")
        return "Success"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def principal():
    """P."""
    # pylint: disable=import-outside-toplevel

    from flask import g

    try:
        identity = g.identity
        return repr(identity).replace("<", "&lt;").replace(">", "&gt;")
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def add_role():
    """A."""
    # pylint: disable=import-outside-toplevel
    # TODO: this todo serves as a reminder for implementing role-adding via GUI

    from invenio_accounts.cli import roles_add

    roles_add = roles_add.callback.__wrapped__  # .__wrapped__

    try:
        roles_add(user="admin@tugraz.at", role="admin")
        return "Success"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def upgrade_db():
    """U."""
    # pylint: disable=import-outside-toplevel

    from copy import deepcopy

    from invenio_db import db

    from ..records.models import LOMDraftMetadata, LOMRecordMetadata

    try:
        # update SQL-database
        schema_key = "$schema"
        schema_str = "local://lomrecords/records/record-v1.0.0.json"

        # update drafts
        for draft in LOMDraftMetadata.query.all():
            old_json = draft.json
            if not old_json:
                # if draft was published, its json is None or empty
                # in that case, nothing need be done
                continue

            if old_json.get(schema_key):
                # if draft already has a schema_key, don't overwrite
                continue

            # to guarantee SQLAlchemy recognizes that json need be updated, make a new object
            new_json = deepcopy(old_json)

            new_json[schema_key] = schema_str
            draft.json = new_json
            db.session.add(draft)

        # update records
        for record in LOMRecordMetadata.query.all():
            old_json = record.json
            if not old_json:
                # if record got a new version, its json is None or empty
                # in that case, nothing need be done
                continue

            if old_json.get(schema_key):
                # if draft already has a schema_key, don't overwrite
                continue

            # to guarantee SQLAlchemy recognizes that json need be updated, make a new object
            new_json = deepcopy(old_json)

            new_json[schema_key] = schema_str
            record.json = new_json
            db.session.add(record)

        db.session.commit()

        # NOTE: don't forget to reindex records in opensearch via `invenio lom rebuild-index`

        return "Success, don't forget to update opensearch-indices too."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def upgrade_db_2():
    """U."""
    # pylint: disable=import-outside-toplevel

    from copy import deepcopy

    from invenio_db import db

    from ..records.models import LOMDraftMetadata, LOMRecordMetadata

    try:
        # update SQL-database

        # update drafts
        for draft in LOMDraftMetadata.query.all():
            old_json = draft.json
            if not old_json:
                # if draft was published, its json is None or empty
                # in that case, nothing need be done
                continue

            if "metadata" not in old_json:
                # not sure this can really happen, just to be safe
                continue

            if "type" not in old_json["metadata"]:
                # 'type' has alreaddy been deleted from db, or was never there
                continue

            # to guarantee SQLAlchemy recognizes that json need be updated, make a new object
            new_json = deepcopy(old_json)

            del new_json["metadata"][
                "type"
            ]  # keys are guaranteed to exist by the above ifs
            draft.json = new_json
            db.session.add(draft)

        # update records
        for record in LOMRecordMetadata.query.all():
            old_json = record.json
            if not old_json:
                # if record got a new version, its json is None or empty
                # in that case, nothing need be done
                continue

            if "metadata" not in old_json:
                # not sure this can really happen, just to be safe
                continue

            if "type" not in old_json["metadata"]:
                # 'type' has alreaddy been deleted from db, or was never there
                continue

            # to guarantee SQLAlchemy recognizes that json need be updated, make a new object
            new_json = deepcopy(old_json)

            del new_json["metadata"][
                "type"
            ]  # keys are guaranteed to exist by the above ifs
            record.json = new_json
            db.session.add(record)

        db.session.commit()

        # NOTE: don't forget to reindex records in opensearch via `invenio lom rebuild-index`

        return "Success, don't forget to update opensearch-indices too."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def reindex():
    """R."""
    # pylint: disable=import-outside-toplevel
    from ..proxies import current_records_lom
    from ..records.models import LOMDraftMetadata, LOMRecordMetadata

    try:
        draft_ids = [
            draft.json["id"]
            for draft in LOMDraftMetadata.query.all()
            if draft.json and "id" in draft.json
        ]
        record_ids = [
            record.json["id"]
            for record in LOMRecordMetadata.query.all()
            if record.json and "id" in record.json
        ]

        service = current_records_lom.records_service
        indexer = service.indexer
        for draft_id in draft_ids:
            draft_api = service.draft_cls.pid.resolve(draft_id, registered_only=False)
            indexer.index(draft_api)
        for record_id in record_ids:
            record_api = service.record_cls.pid.resolve(record_id)
            indexer.index(record_api)

        return "Succesfully reindexed"

    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


# pylint: disable-next=too-many-locals
def xsd():
    """X."""
    # pylint: disable=import-outside-toplevel
    import os
    from pathlib import Path

    from invenio_oaiserver import response as xml
    from lxml import etree

    former_path = os.getcwd()
    try:
        # get parser
        path = Path("/home/obersteiner/documentation/jupyter-notebooks/lom-uibk.xsd")
        os.chdir(path.parent)  # s.t. lxml can find the referenced `xml.xsd`
        xsd_bytes = path.read_bytes()
        xsd_etree = etree.XML(xsd_bytes)
        xsd_schema = etree.XMLSchema(xsd_etree)

        parser = etree.XMLParser(schema=xsd_schema)

        # get records, cf `invenio_oaiserver.views.server:response`
        args = {"metadataPrefix": "lom", "verb": "ListRecords"}
        namespaces = {
            "lom": "https://oer-repo.uibk.ac.at/lom",
            "oai": "http://www.openarchives.org/OAI/2.0/",
        }
        result = getattr(xml, args["verb"].lower())(**args)
        loms = result.xpath("//lom:lom", namespaces=namespaces)

        # validate by parsing with schemaed parser
        messages = []
        for lom in loms:
            # get id
            for id_ in lom.xpath("lom:general/lom:identifier", namespaces=namespaces):
                catalogs = id_.xpath("lom:catalog", namespaces=namespaces)
                if any(catalog.text == "repo-pid" for catalog in catalogs):
                    id_str = ", ".join(
                        ls.text
                        for ls in id_.xpath(
                            "lom:entry/lom:langstring", namespaces=namespaces
                        )
                    )
                    break
            else:
                id_str = "<couldn't find id>"
            lom_str = etree.tostring(lom)
            try:
                etree.fromstring(lom_str, parser)  # validate
                messages.append(f"{id_str}: Success")
            except Exception as e:  # pylint: disable=broad-exception-caught
                messages.append(f"{id_str}: {repr(e)}")

        msg_str = "\n".join(messages)
        return (
            f'<div style="white-space:pre-wrap;font-family=monospace">{msg_str}</div>'
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)
    finally:
        os.chdir(former_path)


def add_pids():
    """A."""
    # pylint: disable=import-outside-toplevel
    from flask import current_app
    from invenio_access.permissions import system_identity
    from invenio_rdm_records.services.pids import providers

    from ..proxies import current_records_lom
    from ..services.services import LOMRecordService
    from ..utils import LOMMetadata

    try:
        current_app.config["LOM_PERSISTENT_IDENTIFIER_PROVIDERS"].append(
            providers.ExternalPIDProvider("new", "new", label="test pid")
        )
        current_app.config["LOM_PERSISTENT_IDENTIFIERS"]["new"] = {
            "providers": ["new"],
            "required": False,
            "label": "new test pid",
        }

        pids = {"new": {"provider": "new", "identifier": "test-id"}}
        data = LOMMetadata.create("unit", pids=pids).json

        service: LOMRecordService = current_records_lom.records_service
        service.create(data=data, identity=system_identity)

        # service.publish will (via uow-task) schedule the celery task register_or_update_pids

        return "Success"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def publish_pids():
    """P."""
    # pylint: disable=import-outside-toplevel
    from flask import current_app
    from invenio_access.permissions import system_identity
    from invenio_rdm_records.services.pids import providers

    from ..proxies import current_records_lom
    from ..services.services import LOMRecordService
    from ..services.tasks import register_or_update_pid as register_task

    pid: str = "jsd62-v2810"
    register = register_task.__wrapped__

    try:
        current_app.config["LOM_PERSISTENT_IDENTIFIER_PROVIDERS"].append(
            providers.ExternalPIDProvider("new", "new", label="test pid")
        )
        current_app.config["LOM_PERSISTENT_IDENTIFIERS"]["new"] = {
            "providers": ["new"],
            "required": False,
            "label": "new test pid",
        }
        # these also were added at some point for further tests:
        # current_app.config["LOM_PERSISTENT_IDENTIFIER_PROVIDERS"].append(
        #     providers.ExternalPIDProvider("cli", "cli", label="cli test pid")
        # )
        # current_app.config["LOM_PERSISTENT_IDENTIFIERS"]["cli"] = {
        #     "providers": ["cli"],
        #     "required": False,
        #     "label": "new cli test pid",
        # }

        service: LOMRecordService = current_records_lom.records_service
        service.publish(id_=pid, identity=system_identity)

        register(recid=pid, scheme="new")

        return "Success"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)


def store_vocabs_on_setup():
    """S."""
    # pylint: disable=import-outside-toplevel
    import os

    from invenio_cli.commands.services import ServicesCommands
    from invenio_cli.helpers.cli_config import CLIConfig
    from invenio_rdm_records.cli import FixturesEngine, system_identity

    former_wd = os.getcwd()
    try:
        os.chdir("/home/obersteiner/environments/v11-dev/repo")

        config = CLIConfig("/home/obersteiner/environments/v11-dev/repo")
        commands = ServicesCommands(config)
        steps = commands.setup(False, True, False, True)
        fixtures_cmd = steps[9].cmd
        print(fixtures_cmd)
        # `fixtures_cmd` is `["pipenv", "run", "invenio", "rdm", "fixtures"]`
        # usually a subprocess executes that via `step.execute`, passing current environment | {PIPENV_VERBOSITY:-1}
        # ignoring the verbosity, `... create fixtures` does as follows:

        FixturesEngine(system_identity).run()

        return "Success"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)
    finally:
        os.chdir(former_wd)


def import_other():
    """I."""
    # pylint: disable=import-outside-toplevel
    from importlib import resources

    import yaml

    from ..fixtures import data

    try:
        with resources.open_text(data.__package__, "vocabularies.yaml") as stream:
            data = yaml.safe_load(stream)
        return repr(data)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return repr(e)
