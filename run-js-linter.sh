#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Usage:
#   ./run-js-linter.sh [args]

# Arguments:
#   -i|--install: install eslint-config-invenio into the nearest node_modules folder
#   -f|--fix: apply formatting to files instead of just checking

# ANSI colors for terminal
GREEN='\033[0;32m'  # green color from here
RED='\033[0;31m'  # red color from here
NC='\033[0m'  # "no color"; turn off colors 

for arg in $@; do
    case ${arg} in
        -i|--install)
            npm install --no-save --no-package-lock @inveniosoftware/eslint-config-invenio@^2.0.0
            ;;
        -f|--fix)
            printf "${GREEN}Formatting with eslint...${NC}\n"  # TODO: consider removing this line...
            npx eslint -c .eslintrc.yml invenio_records_lom/**/*.js --fix
            ;;
        *)
            printf "${RED}Unknown argument: $arg${NC}\n"
            exit
            ;;
        esac
done

printf "${GREEN}Running eslint...${NC}\n"
npx eslint -c .eslintrc.yml invenio_records_lom/**/*.js
