#!/bin/bash
BOFH_PATH="$( dirname -- "$( readlink -f -- "$0"; )"; )"
sed -i 's/\./ /g' "$BOFH_PATH"/data/unreachableNodes.txt
sort -b -k2,2 -k1,1 -o "$BOFH_PATH"/data/unreachableNodes.txt{,}
sed -i 's/ /\./g' "$BOFH_PATH"/data/unreachableNodes.txt
