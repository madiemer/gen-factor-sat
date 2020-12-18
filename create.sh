#!/bin/bash
source $1
out_dir=$2
random=${3:-false}

function create_instances {
    log_dir=$1
    numbers=$2

    mkdir -p $log_dir
    for number in ${numbers[@]}
    do
      python3 -m gen_factor_sat number $number -o $log_dir
    done
}

function create_random_instances {
    log_dir=$1
    max_value=$2
    numbers=$3

    mkdir -p $log_dir
    for ((i = 0; i < $numbers; i++))
    do
      python3 -m gen_factor_sat random $max_value -o $log_dir
    done
}


mkdir -p $out_dir
for index in "${!NAMES[@]}"
do
  log_dir="${out_dir}/${NAMES[$index]}"

  if [ "$random" = true ]
  then
    max_value="${MAX_VALUES[$index]}"
    iterations="${ITERATIONS[$index]}"
    create_random_instances "${log_dir}" "${max_value}" "${iterations}"
  else
    numbers="${NUMBERS[$index]}"
    create_instances "${log_dir}" "${numbers}"
  fi
done

