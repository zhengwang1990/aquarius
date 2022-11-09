#!/bin/bash
bin_dir=$(dirname "$0")
if [[ ${bin_dir} == "." ]]
then
  base_dir=".."
else
  base_dir=$(dirname "$bin_dir")
fi

directories=("${base_dir}/cache/DAY" "${base_dir}/cache/stock_universe"/* "${base_dir}/outputs/trading")
for directory in "${directories[@]}"
do
  if [[ -d "${directory}" ]]
  then
    for filename in "${directory}"/*
    do
      days_to_live=$(( 7 - ($(date +%s) - $(stat -c %Y "${filename}")) / 86400 ))
      if [[ ${days_to_live} -le 0 ]]
      then
        rm -rf "${filename}"
      fi
    done
  fi
done
