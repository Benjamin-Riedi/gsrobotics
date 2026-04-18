#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${1:-${REPO_ROOT}/examples/rgb_ros1_noetic_config.json}"

# shellcheck disable=SC1091
source /opt/ros/noetic/setup.bash

python3 "${REPO_ROOT}/ros1_rgb_publisher.py" --config "${CONFIG_PATH}"
