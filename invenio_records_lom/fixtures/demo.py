# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Fake LOM demo records."""

import json

from faker import Faker
from flask_principal import Identity
from invenio_access import any_user

from ..proxies import current_records_lom


# ----- functions for LOM datatypes -----
def langstringify(fake: Faker, string: str) -> dict:
    """Wraps `string` in a dict, emulating LOMv1.0-standard LangString-objects."""
    return {
        "language": create_fake_language(fake),
        "string": string,
    }


def vocabularify(fake: Faker, choices: list) -> dict:
    """Randomly draw a choice from `choices`, then wrap that choice in a dict, emulating LOMv1.0-standard Vocabulary-objects."""
    return {
        "source": "LOMv1.0",
        "value": fake.random.choice(choices),
    }


def create_fake_datetime(fake: Faker) -> dict:
    """Create a fake datetime dict, as per LOMv1.0-standard Datetime-object-specification."""
    pattern = fake.random.choice(["YMDhmsTZD", "YMDhms", "YMD", "Y"])
    if pattern == "Y":
        datetime = fake.year()
    elif pattern == "YMD":
        datetime = fake.date()
    elif pattern == "YMDhms":
        datetime = fake.date_time().isoformat()
    elif pattern == "YMDhmsTZD":
        time_zone_designator = fake.pytimezone()
        datetime = fake.date_time(tzinfo=time_zone_designator).isoformat()

    return {"dateTime": datetime, "description": langstringify(fake, fake.sentence())}


def create_fake_duration(fake: Faker) -> dict:
    """Create a fake duration dict, as per LOMv1.0-standard Duration-object-specification."""
    random = fake.random
    pattern = random.choice(["all", "Y", "D", "HM", "S"])
    duration = {
        "all": "P1Y2M4DT10H35M12.5S",
        "Y": f"P{random.randint(1,5)}Y",
        "D": f"P{random.randint(1,60)}D",
        "HM": f"PT{random.randint(1,3)}H{random.randint(1,59)}M",
        "S": f"PT{random.uniform(0.1, 12.5)}S",
    }

    return {
        "duration": duration[pattern],
        "description": langstringify(fake, fake.sentence()),
    }


def create_fake_vcard(fake: Faker) -> str:
    """Returns a placeholder-string for a vCard-object."""
    return "placeholder for vcard"


# ----- functions for elements that are part of more than one category -----
def create_fake_language(fake: Faker) -> str:
    """Create a fake language-code, as required for "language"-keys by LOMv1.0-standard."""
    language_codes = [
        "EN",
        "en-us",
        "en-US-philadelphia",
        "eng",
        "eng-US",
        "ENG-us-philadelphia",
    ]
    return fake.random.choice(language_codes)


def create_fake_identifier(fake: Faker) -> dict:
    """Create a fake "identifier"-element, compatible with LOMv1.0-standard."""
    catalog = fake.random.choice(["URI", "ISBN"])
    if catalog == "URI":
        entry = fake.uri()
    else:
        entry = fake.isbn13()

    return {
        "catalog": catalog,
        "entry": entry,
    }


def create_fake_contribute(fake: Faker, roles: list) -> dict:
    """Create a fake "contribute"-element, compatible with LOMv1.0-standard."""
    return {
        "role": vocabularify(fake, roles),
        "entity": [create_fake_vcard(fake) for __ in range(2)],
        "date": create_fake_datetime(fake),
    }


# ----- functions for categories or used by only one category -----
def create_fake_general(fake: Faker) -> dict:
    """Create a fake "general"-element, compatible with LOMv1.0-standard."""
    structures = ["atomic", "collection", "networked", "hierarchical", "linear"]
    aggregationLevels = ["1", "2", "3", "4"]

    return {
        "identifier": [create_fake_identifier(fake) for __ in range(2)],
        "title": langstringify(fake, " ".join(fake.words())),
        "language": [fake.random.choice([create_fake_language(fake), "none"])],
        "description": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        "keyword": [langstringify(fake, fake.word()) for __ in range(2)],
        "coverage": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        "structure": vocabularify(fake, structures),
        "aggregationLevel": vocabularify(fake, aggregationLevels),
    }


def create_fake_lifecycle(fake: Faker) -> dict:
    """Create a fake "lifeCycle"-element, compatible with LOMv1.0-standard."""
    roles = [
        "author",
        "publisher",
        "unknown",
        "initiator",
        "terminator",
        "validator",
        "editor",
        "graphical designer",
        "technical implementer",
        "content provider",
        "technical validator",
        "educational validator",
        "script writer",
        "instructional designer",
        "subject matter expert",
    ]

    statuses = ["draft", "final", "revised", "unavailable"]

    random_int = fake.random.randint

    return {
        "version": langstringify(fake, f"{random_int(0,9)}.{random_int(0,9)}"),
        "status": vocabularify(fake, statuses),
        "contribute": [create_fake_contribute(fake, roles) for __ in range(2)],
    }


def create_fake_metametadata(fake: Faker) -> dict:
    """Create a fake "metaMetadata"-element, compatible with LOMv1.0-standard."""
    roles = ["creator", "validator"]
    return {
        "identifier": [create_fake_identifier(fake) for __ in range(2)],
        "contribute": [create_fake_contribute(fake, roles) for __ in range(2)],
        "metadataSchemas": ["LOMv1.0"],
        "language": create_fake_language(fake),
    }


def create_fake_technical(fake: Faker) -> dict:
    """Create a fake "technical"-element, compatible with LOMv1.0-standard."""
    return {
        "format": [fake.random.choice([fake.mime_type(), "non-digital"])],
        "size": str(fake.random.randint(1, 2 ** 32)),
        "location": [
            fake.uri(),
        ],
        "requirement": [create_fake_requirement(fake) for __ in range(2)],
        "installationRemarks": langstringify(fake, fake.paragraph()),
        "otherPlatformRequirements": langstringify(fake, fake.paragraph()),
    }


def create_fake_requirement(fake: Faker) -> dict:
    """Create a fake "requirement"-element, compatible with LOMv1.0-standard."""
    return {
        "orComposite": [create_fake_orcomposite(fake) for __ in range(2)],
    }


def create_fake_orcomposite(fake: Faker) -> dict:
    """Create a fake "orComposite"-element, compatible with LOMv1.0-standard."""
    type_ = fake.random.choice(["operating system", "browser"])
    if type_ == "operating system":
        requirement_names = [
            "pc-dos",
            "ms-windows",
            "macos",
            "unix",
            "multi-os",
            "none",
        ]
    else:
        requirement_names = [
            "any",
            "netscape communicator",
            "ms-internet explorer",
            "opera",
            "amaya",
        ]

    return {
        "type": vocabularify(fake, [type_]),
        "name": vocabularify(fake, requirement_names),
        "minimumVersion": str(fake.random.randint(1, 4)),
        "maximumVersion": str(fake.random.randint(5, 8)),
    }


def create_fake_educational(fake: Faker) -> dict:
    """Create a fake "educational"-element, compatible with LOMv1.0-standard."""
    interactivity_types = ["active", "expositive", "mixed"]
    learning_resource_types = [
        "exercise",
        "simulation",
        "questionnaire",
        "diagram",
        "figure",
        "graph",
        "index",
        "slide",
        "table",
        "narrative text",
        "exam",
        "experiment",
        "problem statement",
        "self assessment",
        "lecture",
    ]
    levels = ["very low", "low", "medium", "high", "very high"]
    difficulties = ["very easy", "easy", "medium", "difficult", "very difficult"]
    end_user_roles = ["teacher", "author", "learner", "manager"]
    contexts = ["school", "higher education", "training", "other"]

    random_int = fake.random.randint

    return {
        "interactivityType": vocabularify(fake, interactivity_types),
        "learningResourceType": vocabularify(fake, learning_resource_types),
        "interactivityLevel": vocabularify(fake, levels),
        "semanticDensity": vocabularify(fake, levels),
        "intendedEndUserRole": vocabularify(fake, end_user_roles),
        "context": vocabularify(fake, contexts),
        "typicalAgeRange": langstringify(fake, f"{random_int(1,4)}-{random_int(5,9)}"),
        "difficulty": vocabularify(fake, difficulties),
        "typicalLearningTime": create_fake_duration(fake),
        "description": langstringify(fake, fake.paragraph()),
        "language": [create_fake_language(fake) for __ in range(2)],
    }


def create_fake_rights(fake: Faker) -> dict:
    """Create a fake "rights"-element, compatible with LOMv1.0-standard."""
    return {
        "cost": vocabularify(fake, ["yes", "no"]),
        "copyrightAndOtherRestrictions": vocabularify(fake, ["yes", "no"]),
        "description": langstringify(fake, fake.paragraph()),
    }


def create_fake_relation(fake: Faker) -> dict:
    """Create a fake "relation"-element, compatible with LOMv1.0-standard."""
    kinds = [
        "ispartof",
        "haspart",
        "isversionof",
        "hasversion",
        "isformatof",
        "hasformat",
        "references",
        "isreferencedby",
        "isbasedon",
        "isbasisfor",
        "requires",
        "isrequiredby",
    ]

    return {
        "kind": vocabularify(fake, kinds),
        "resource": {
            "identifier": [create_fake_identifier(fake) for __ in range(2)],
            "description": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        },
    }


def create_fake_annotation(fake: Faker) -> dict:
    """Create a fake "annotation"-element, compatible with LOMv1.0-standard."""
    return {
        "entity": create_fake_vcard(fake),
        "date": create_fake_datetime(fake),
        "description": langstringify(fake, fake.paragraph()),
    }


def create_fake_classification(fake: Faker) -> dict:
    """Create a fake "classification"-element, compatible with LOMv1.0-standard."""
    purposes = [
        "discipline",
        "idea",
        "prerequisite",
        "educational objective",
        "accessability restrictions",
        "educational level",
        "skill level",
        "security level",
        "competency",
    ]

    return {
        "purpose": vocabularify(fake, purposes),
        "taxonPath": [create_fake_taxonpath(fake) for __ in range(2)],
        "description": langstringify(fake, fake.paragraph()),
        "keyword": langstringify(fake, fake.word()),
    }


def create_fake_taxonpath(fake: Faker) -> dict:
    """Create a fake "taxonPath"-element, compatible with LOMv1.0-standard."""
    return {
        "source": langstringify(fake, fake.word()),
        "taxon": [create_fake_taxon(fake) for __ in range(2)],
    }


def create_fake_taxon(fake: Faker) -> dict:
    """Create a fake "taxon"-element, compatible with LOMv1.0-standard."""
    return {
        "id": fake.lexify(
            "?????",
            letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ.0123456789",
        ),
        "entry": langstringify(fake, fake.word()),
    }


# ----- functions for creating LOMv1.0-fakes -----
def create_fake_metadata(fake: Faker) -> dict:
    """Create a fake json-representation of a "lom"-element, compatible with LOMv1.0-standard."""
    data_to_use = {
        "general": create_fake_general(fake),
        "lifeCycle": create_fake_lifecycle(fake),
        "metaMetadata": create_fake_metametadata(fake),
        "technical": create_fake_technical(fake),
        "educational": [create_fake_educational(fake) for __ in range(2)],
        "rights": create_fake_rights(fake),
        "relation": [create_fake_relation(fake) for __ in range(2)],
        "annotation": [create_fake_annotation(fake) for __ in range(2)],
        "classification": [create_fake_classification(fake) for __ in range(2)],
    }

    return json.loads(json.dumps(data_to_use))


def create_fake_record(fake: Faker):
    """Enter fake records in the SQL-database."""
    # invenio user identities have integers as `id`s, use a string to avoid collisions
    fake_identity = Identity(id="lom_demo")
    fake_identity.provides.add(any_user)

    fake_access_type = fake.random.choice(["public", "restricted"])

    has_embargo = fake.boolean()
    if has_embargo:
        fake_embargo = {
            "until": fake.future_date(end_date="+365d").isoformat(),
            "reason": "Fake embargo for fake record.",
            "active": True,
        }
    else:
        fake_embargo = {}

    fake_access = {
        "files": fake_access_type,
        "record": fake_access_type,
        "embargo": fake_embargo,
    }

    data = {
        # these values get processed by service.config.components
        "access": fake_access,
        "metadata": create_fake_metadata(fake),
    }

    service = current_records_lom.records_service
    draft = service.create(data=data, identity=fake_identity)
    service.publish(id_=draft.id, identity=fake_identity)


def create_fake_records(number: int, seed: int = 42) -> list:
    """Create `number` jsons adhering to LOMv1.0-standard, using `seed` as RNG-seed."""
    fake = Faker()
    Faker.seed(seed)

    return [create_fake_record(fake) for __ in range(number)]
