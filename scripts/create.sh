#!/bin/bash
source $1
OUT_DIR=$2
GENERATE=${3:-false}

function create_instances {
    directory=$1
    numbers=$2

    mkdir -p $directory
    for number in ${numbers[@]}
    do
      python3 -m gen_factor_sat number $number -o $directory
    done
}

function create_random_instances {
    directory=$1
    min_value=$2
    max_value=$3
    numbers=$4

    mkdir -p $directory
    for ((i = 0; i < $numbers; i++))
    do
      python3 -m gen_factor_sat random --min-value $min_value $max_value -o $directory
    done
}


mkdir -p $OUT_DIR
for index in "${!SUBDIRECTORIES[@]}"
do
  directory="${OUT_DIR}/${SUBDIRECTORIES[$index]}"

  if [ "$GENERATE" = true ]
  then
    min_value="${MIN_VALUES[$index]}"
    max_value="${MAX_VALUES[$index]}"
    iterations="${ITERATIONS[$index]}"
    create_random_instances "${directory}" "${min_value}" "${max_value}" "${iterations}"
  else
    numbers="${NUMBERS[$index]}"
    create_instances "${directory}" "${numbers}"
  fi
done

