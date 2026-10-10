#!/usr/bin/env bash
set -euo pipefail
version=4.2.0
archive="blender-${version}-linux-x64.tar.xz"
base=https://download.blender.org/release/Blender4.2
mkdir -p "$RUNNER_TEMP/blender-install"
cd "$RUNNER_TEMP/blender-install"
curl --fail --location --retry 3 "$base/$archive" -o "$archive"
curl --fail --location --retry 3 "$base/blender-${version}.sha256" -o checksums.txt
grep " $archive$" checksums.txt > selected.sha256
sha256sum --check selected.sha256
tar -xf "$archive"
echo "$PWD/blender-${version}-linux-x64" >> "$GITHUB_PATH"
