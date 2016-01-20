#!/usr/bin/env bash

cd "$(dirname $(readlink -f $0))"

pandoc -t json -s  $1_original.md |\
 tee $1_original.json |\
 ../minted.exe |\
 tee $1_result.json |\
 pandoc -f json -t latex -o $1_result.tex
