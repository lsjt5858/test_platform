#!/usr/bin/env bash
# Simple runner to execute pytest by domain(s) and generate Allure report under test/reports/
# Usage example:
#   ./bears_run.sh \
#     --testcase=domain/enterprise,domain/open_api \
#     --product=ce --env=800 --store=True --zone=onprem \
#     --report=True --only-rerun=AttributeError,AssertionError \
#     --processes=1

set -euo pipefail

# Defaults (run with reasonable defaults if no args passed)
TESTCASE="domain/enterprise"
PRODUCT="ce"
ENV_VAL="800"
STORE="True"
ZONE="onprem"
REPORT="True"
ONLY_RERUN=""
PROCESSES="1"
DISPLAY_ENV=""  # optional: override Env shown in environment.properties

# Parse args
for arg in "$@"; do
  case $arg in
    --testcase=*) TESTCASE=${arg#*=} ;;
    --product=*) PRODUCT=${arg#*=} ;;
    --env=*) ENV_VAL=${arg#*=} ;;
    --store=*) STORE=${arg#*=} ;;
    --zone=*) ZONE=${arg#*=} ;;
    --report=*) REPORT=${arg#*=} ;;
    --only-rerun=*) ONLY_RERUN=${arg#*=} ;;
    --processes=*) PROCESSES=${arg#*=} ;;
    --display-env=*) DISPLAY_ENV=${arg#*=} ;;
    *) echo "[warn] unknown arg: $arg" ;;
  esac
done

# If no args provided, run defaults silently

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_PY="$ROOT_DIR/nut_venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  VENV_PY=$(command -v python3 || command -v python)
fi

export PYTHONPATH="$ROOT_DIR/core/src:$ROOT_DIR/app/src"

# 1) Apply base config so code under test picks env/product/zone/store
"$VENV_PY" - <<PY
from core.base_util.config_util import ConfigUtil
ConfigUtil.reload()
ConfigUtil.update_base('product', '${PRODUCT}')
ConfigUtil.update_base('env', '${ENV_VAL}')
ConfigUtil.update_base('store', '${STORE}')
ConfigUtil.update_base('zone', '${ZONE}')
print('[info] Updated base config to product=${PRODUCT}, env=${ENV_VAL}, store=${STORE}, zone=${ZONE}')
PY

# Helper: check if xdist is available for -n
HAVE_XDIST=0
"$VENV_PY" - <<'PY' >/dev/null 2>&1 || true
import sys
try:
    import xdist  # type: ignore
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
if [[ $? -eq 0 ]]; then HAVE_XDIST=1; fi

IFS=',' read -r -a CASE_ITEMS <<< "$TESTCASE"

# Build pytest targets list (files/dirs). Accept forms:
#  - domain/foo[/...][::node]
#  - test/domain/foo[/...][::node]
#  - any relative/absolute pytest target
TARGETS=()
DOMAIN_LIST=()
for raw in "${CASE_ITEMS[@]}"; do
  item="$raw"
  node_suffix=""
  if [[ "$item" == *"::"* ]]; then
    node_suffix="::${item#*::}"
    item="${item%%::*}"
  fi

  if [[ "$item" == /* ]]; then
    target="$item$node_suffix"
  elif [[ "$item" == test/* ]]; then
    target="$ROOT_DIR/$item$node_suffix"
  elif [[ "$item" == domain/* ]]; then
    target="$ROOT_DIR/test/$item$node_suffix"
  else
    # short form like "enterprise" or "enterprise/api"
    target="$ROOT_DIR/test/domain/$item$node_suffix"
  fi
  TARGETS+=("$target")
  # collect domain name for environment.properties display
  # pick first segment after test/domain/
  dom_path="${target#*$ROOT_DIR/test/domain/}"
  dom_name="${dom_path%%/*}"
  DOMAIN_LIST+=("$dom_name")
done

RESULTS_DIR="$ROOT_DIR/test/reports/.allure_results_tmp"
REPORT_DIR="$ROOT_DIR/test/reports/latest"
rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR" "$REPORT_DIR"

PYTEST_ARGS=("--alluredir" "$RESULTS_DIR" "--color=yes")
PYTEST_ARGS+=("${TARGETS[@]}")

# Optional: mark filter
if [[ -n "${MARK:-}" ]]; then
  PYTEST_ARGS+=("-m" "$MARK")
fi

# processes and dist
if [[ "$PROCESSES" =~ ^[0-9]+$ ]] && [[ "$PROCESSES" -gt 1 ]] && [[ $HAVE_XDIST -eq 1 ]]; then
  PYTEST_ARGS+=("-n" "$PROCESSES")
  if [[ -n "${DIST:-}" ]]; then
    PYTEST_ARGS+=("--dist" "$DIST")
  fi
fi

# reruns support if plugin installed
HAVE_RERUNS=0
"$VENV_PY" - <<'PY' >/dev/null 2>&1 || true
import sys
try:
    import pytest_rerunfailures  # type: ignore
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
if [[ $? -eq 0 ]]; then HAVE_RERUNS=1; fi

if [[ $HAVE_RERUNS -eq 1 ]]; then
  if [[ -n "${RERUNS:-}" ]] && [[ "$RERUNS" =~ ^[0-9]+$ ]] && [[ "$RERUNS" -gt 0 ]]; then
    PYTEST_ARGS+=("--reruns" "$RERUNS")
  fi
  if [[ -n "$ONLY_RERUN" ]]; then
    PYTEST_ARGS+=("--only-rerun" "$ONLY_RERUN")
  fi
else
  if [[ -n "${RERUNS:-}" ]] || [[ -n "$ONLY_RERUN" ]]; then
    echo "[warn] pytest-rerunfailures not installed; rerun options will be ignored"
  fi
fi

echo "[info] Running pytest with targets: ${TARGETS[*]}"
set +e
"$VENV_PY" -m pytest "${PYTEST_ARGS[@]}"
PYTEST_RC=$?
set -e

# 2) Inject environment.properties for Allure
[[ -n "$DISPLAY_ENV" ]] && ENV_SHOW="$DISPLAY_ENV" || ENV_SHOW="$ENV_VAL"
uniq_domains=$(printf '%s\n' "${DOMAIN_LIST[@]}" | awk '!a[$0]++' | paste -sd, -)
cat > "$RESULTS_DIR/environment.properties" <<ENV
Env=${ENV_SHOW}
Zone=${ZONE}
Product=${PRODUCT}
Store=${STORE}
Domains=${uniq_domains}
ENV

# 3) Generate Allure report, preserving history by using previous report as input
if command -v allure >/dev/null 2>&1; then
  if [[ -d "$REPORT_DIR/history" ]]; then
    allure generate --clean "$REPORT_DIR" "$RESULTS_DIR" -o "$REPORT_DIR"
  else
    allure generate --clean "$RESULTS_DIR" -o "$REPORT_DIR"
  fi
  echo "[info] Allure report generated: $REPORT_DIR/index.html"
else
  echo "[warn] 'allure' cli not found. Results kept at: $RESULTS_DIR"
fi

echo "[done] All targets processed."
exit ${PYTEST_RC}
