#!/usr/bin/env bash
# NativeAOT cross-builds Android from Linux; no game files or keys are needed.
set -euo pipefail
if [[ $(uname -s) != Linux ]]; then echo "Android NativeAOT requires a Linux build host" >&2; exit 1; fi
: "${ANDROID_NDK_HOME:?Set ANDROID_NDK_HOME}"
: "${OUT:?Set OUT to the build output directory}"
task_here=$(cd "$(dirname "$0")" && pwd)
task_host=linux-x86_64
task_bin="$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/$task_host/bin"
task_dotnet=${DOTNET:-dotnet}
export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_CLI_TELEMETRY_OPTOUT=1
"$task_dotnet" publish "$task_here/nx_extract_aot.csproj" -c Release -o "$OUT" \
    -p:CppCompilerAndLinker="$task_bin/aarch64-linux-android31-clang" -p:ObjCopyName="$task_bin/llvm-objcopy"
