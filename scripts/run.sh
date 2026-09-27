#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export DOTNET_CLI_HOME="$PWD/.tools"
export DOTNET_CLI_TELEMETRY_OPTOUT=1
DOTNET="${DOTNET:-$PWD/.tools/dotnet/dotnet}"
if [ ! -x "$DOTNET" ]; then DOTNET=dotnet; fi
export CUSTOMER_TOKEN="${CUSTOMER_TOKEN:-demo-customer-token-change-me-001}"
export CUSTOMER2_TOKEN="${CUSTOMER2_TOKEN:-demo-customer-token-change-me-002}"
export PARTNER_TOKEN="${PARTNER_TOKEN:-demo-partner-token-change-me-001}"
export OPERATOR_TOKEN="${OPERATOR_TOKEN:-demo-operator-token-change-me-001}"
export DEMO_PASSWORD="${DEMO_PASSWORD:-WaterDemo2026!}"
export ASPNETCORE_ENVIRONMENT=Development
PORT_BASE="${PORT_BASE:-5100}"
DATA_ROOT="${DATA_ROOT:-$PWD/.data}"
export USAGE_URL="http://127.0.0.1:$((PORT_BASE+1))" PAYMENTS_URL="http://127.0.0.1:$((PORT_BASE+2))"
mkdir -p "$DATA_ROOT" evidence
pids=()
cleanup(){ for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM
DATA_PATH="$DATA_ROOT/usage.db" "$DOTNET" src/Water.Usage/bin/Debug/net10.0/Water.Usage.dll --urls "$USAGE_URL" > evidence/usage.log 2>&1 & pids+=("$!")
DATA_PATH="$DATA_ROOT/payments.db" "$DOTNET" src/Water.Payments/bin/Debug/net10.0/Water.Payments.dll --urls "$PAYMENTS_URL" > evidence/payments.log 2>&1 & pids+=("$!")
"$DOTNET" src/Water.Portal/bin/Debug/net10.0/Water.Portal.dll --contentRoot "$PWD/src/Water.Portal" --urls "http://127.0.0.1:$PORT_BASE" > evidence/portal.log 2>&1 & pids+=("$!")
printf 'WaterLink: http://127.0.0.1:%s\nDemo password: WaterDemo2026! (unless overridden)\n' "$PORT_BASE"
printf '%s\n' "${pids[@]}" > "$DATA_ROOT/runtime.pids"
wait
