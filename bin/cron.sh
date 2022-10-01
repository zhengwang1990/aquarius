#/bin/bash
base_dir=$(dirname "$0")
rm -f "${base_dir}/console.txt"

directories=("${base_dir}/cache/DAY" "${base_dir}/outputs/trading")
for directory in "${directories[@]}"
do
  for filename in "${directory}"/*
  do
    days_to_live=$(( 90 - ($(date +%s) - $(stat -c %Y "${filename}")) / 86400 ))
    if [[ ${days_to_live} -le 0 ]]
    then
      rm -rf "${filename}"
    fi
  done
done

ln -sf "${base_dir}/outputs/trading/$(date +'%Y-%m-%d')/log.txt" "${base_dir}/log.txt"

source "${base_dir}/envs.sh"

python3 "${base_dir}/alpharius/trade.py" --mode "trade" >> "${base_dir}/console.txt" 2>&1

exit_code="$?"
console_file="${base_dir}/console.txt"
console_tail=$(tail "${console_file}")
if [[ "${exit_code}" -ne "0" ]] || [[ ! -z "${console_tail}" ]]
then
  python3 "${base_dir}/alpharius/alert.py" --log_file "${console_file}" --error_code "${exit_code}"
fi
