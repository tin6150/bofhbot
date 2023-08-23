#!/bin/bash
sed -i 's/\./ /g' ~/bofhbot/data/unreachableNodes.txt
sort -b -k2,2 -k1,1 -o ~/bofhbot/data/unreachableNodes.txt{,}
sed -i 's/ /\./g' ~/bofhbot/data/unreachableNodes.txt
