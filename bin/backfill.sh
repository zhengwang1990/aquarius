#!/bin/bash
bin_dir=$(dirname "$0")
if [[ ${bin_dir} == "." ]]
then
  base_dir=".."
else
  base_dir=$(dirname "$bin_dir")
fi
rm -f "${base_dir}/console_backfill.txt"

if [[ -f "${base_dir}/bin/envs.sh" ]]
then
  source "${base_dir}/bin/envs.sh"
fi

python3 "${base_dir}/alpharius/backfill.py" >> "${base_dir}/console_backfill.txt" 2>&1

exit_code="$?"
console_file="${base_dir}/console_backfill.txt"
console_tail=$(tail "${console_file}")
if [[ "${exit_code}" -ne "0" ]] || [[ -n "${console_tail}" ]]
then
  python3 "${base_dir}/alpharius/alert.py" \
  --log_file "${console_file}" \
  --error_code "${exit_code}" \
  --title "Backfilling encountered an unexpected error"
fi