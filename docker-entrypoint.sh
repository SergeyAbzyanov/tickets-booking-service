#!/usr/bin/env sh

case "${1}" in
    "app")
        shift
        echo "Starting API ..." && \
        exec uvicorn src.main:app --host 0.0.0.0
        ;;
    "pytest")
        shift
        echo "Tests"
        exec pytest ${@}
        ;;
    "help")
        shift
        exec echo "Set command: app pytest"
        ;;
    *)
        exec ${@}
        ;;
esac