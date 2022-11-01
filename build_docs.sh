rm -fR docs/api
mkdir -p docs/api
pdoc3 pysspm --html --force --output-dir docs/api --template-dir templates