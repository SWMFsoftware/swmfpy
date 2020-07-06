#!/usr/bin/env bash
# Script to make the changelogs

echo 'Changelog:' > CHANGELOG.markdown
echo '==========' >> CHANGELOG.markdown
echo '' >> CHANGELOG.markdown

echo '' >> CHANGELOG.markdown
echo 'Contributors:' >> CHANGELOG.markdown
echo '-------------' >> CHANGELOG.markdown
echo '' >> CHANGELOG.markdown
git shortlog -n -s >> CHANGELOG.markdown

echo '' >> CHANGELOG.markdown
echo 'Changes:' >> CHANGELOG.markdown
echo '--------' >> CHANGELOG.markdown
echo '' >> CHANGELOG.markdown
git log --oneline --pretty='format:- %h **(%as, %an)**: _C:%D:_ %s' >> CHANGELOG.markdown
