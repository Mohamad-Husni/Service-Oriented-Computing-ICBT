#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DOTNET="${DOTNET:-$PWD/.tools/dotnet/dotnet}"
if [ ! -x "$DOTNET" ]; then DOTNET=dotnet; fi
export DOTNET_CLI_HOME="$PWD/.tools"
export NUGET_PACKAGES="$PWD/.tools/packages"
export DOTNET_CLI_TELEMETRY_OPTOUT=1
"$DOTNET" restore WaterLink.sln --disable-parallel
"$DOTNET" build WaterLink.sln --no-restore -m:1 -p:UsedAvaloniaProducts=
