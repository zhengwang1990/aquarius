#!/bin/bash
bin_dir=$(dirname "$0")
if [[ ${bin_dir} == "." ]]
then
  base_dir=".."
else
  base_dir=$(dirname "$bin_dir")
fi
rm -f "${base_dir}/console_trade.txt"

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

ln -sf "${base_dir}/outputs/trading/$(date +'%Y-%m-%d')/log.txt" "${base_dir}/log.txt"

if [[ -f "${base_dir}/bin/envs.sh" ]]
then
  source "${base_dir}/bin/envs.sh"
fi

python3 "${base_dir}/alpharius/trade.py" --mode "trade" >> "${base_dir}/console_trade.txt" 2>&1

exit_code="$?"
console_file="${base_dir}/console_trade.txt"
console_tail=$(tail "${console_file}")
if [[ "${exit_code}" -ne "0" ]] || [[ -n "${console_tail}" ]]
then
  python3 "${base_dir}/alpharius/alert.py" \
  --log_file "${console_file}" \
  --error_code "${exit_code}" \
  --title "Trading system encountered an unexpected error"
fi
