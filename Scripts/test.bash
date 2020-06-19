#!/bin/env bash
#exit on Error (even within a pipeline) and treat Unset variables as errors
set -euo pipefail
#for tracing
#set -x

DIR_COVERAGE=".htmlcov"
FILE_COVERAGE="index.html"

if [ -z "${VIRTUAL_ENV+x}" ]; then
	echo "Error: the virtual environment is not active"
	exit 1
fi

if [ "${1:-}" == "--coverage" ]; then
	echo running all tests with coverage
	coverage run -m pytest
	status=0
	if [ "${2:-}" = "--fail" ]; then
		set +e
		coverage report --fail-under=100
		status=$?
		set -e
	else
		coverage report
	fi
	coverage html -d "$DIR_COVERAGE"
	echo "Tests complete. Detailed coverage results are located in \"$DIR_COVERAGE/$FILE_COVERAGE\""
	exit $status
elif [ "${1:-}" == "--unit" ]; then
	echo "Running unit tests"
	pytest --exitfirst -m unit
elif [ "${1:-}" == "--integration" ]; then
	echo "Running integration tests"
	pytest --exitfirst -m integration
else
	"$0" --unit || (echo Failed to pass all unit tests; exit 1)
	"$0" --integration || (echo Failed to pass all integration tests; exit 1)
	echo "Passed all tests"
fi
