#!/bin/bash

echo -e "Feynopt for SHA256\n"
for i in {01..64}; do
    echo "[+] Round $i"
    time feynopt -cnotmin -simplify "./sha256/sha256-qasm-$i.qasm" > "./sha256/cnotmin/sha256-qasm-$i-cnotmin.qasm"
done
