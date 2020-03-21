#!/bin/env bash
#exit on Error (even within a pipeline) and treat Unset variables as errors
set -euo pipefail
#for tracing
#set -x

if [ -z "${VIRTUAL_ENV+x}" ]; then
	echo "Error: the virtual environment is not active"
	exit 1
fi

if [ "${1:-}" == "--coverage" ]; then
	echo RUNNING WITH COVERAGE
	coverage run -m pytest
	coverage report
	coverage html -d .htmlcov
else
	echo RUNNING WITHOUT COVERAGE
	pytest
fi
