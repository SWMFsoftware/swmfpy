#!/usr/bin/env bash
# Script to make the changelogs

git log --oneline --pretty='format:- %h **(%as, %an)**: _C%D_: %s' > CHANGELOG.markdown
