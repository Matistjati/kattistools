
VENVPATH="$(dirname "$(dirname "$(readlink -f "$0")")")/venv"

export PYTHONPATH
ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")${PYTHONPATH:+:}"
PYTHONPATH="$ROOT$PYTHONPATH"
$VENVPATH/bin/pip install pytest
$VENVPATH/bin/pip install -e $ROOT
exec "$VENVPATH/bin/python" -m pytest $@
