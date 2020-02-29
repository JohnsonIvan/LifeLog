#!/bin/env bash
#exit on Error (even within a pipeline) and treat Unset variables as errors
set -euo pipefail
#for tracing
#set -x

echo RUNNING TESTS
pytest

if [ "${1:-}" == "--coverage" ]; then
	echo RUNNING COVERAGE
	coverage run -m pytest
	coverage report
	coverage html -d .htmlcov
else
	echo NO COVERAGE
fi
