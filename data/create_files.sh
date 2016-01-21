#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
  cd "$(dirname $(greadlink -f $0))";
else
  cd "$(dirname $(readlink -f $0))"
fi

pandoc -t json -s  $1_original.md |\
 python -m json.tool --sort-keys |\
 tee $1_original.json |\
 ../minted.py |\
 python -m json.tool --sort-keys |\
 tee $1_result.json |\
 pandoc -f json -t latex -o $1_result.tex
