@ECHO OFF
rmdir /S /Q docs\api
md docs\api
pdoc3 pysspm --html --force --output-dir docs\api --template-dir templates