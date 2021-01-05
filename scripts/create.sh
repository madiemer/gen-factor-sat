#!/bin/bash
OUT_DIR=$1

#Start:Stop:Step
IFS=':' read -ra INTERVALS <<< $2
start=${INTERVALS[0]}
stop=${INTERVALS[1]}
step=${INTERVALS[2]}

#Random:Prime:Composite
IFS=':' read -ra NUMBERS <<< $3
num_rand=${NUMBERS[0]}
num_prime=${NUMBERS[1]}
num_comp=${NUMBERS[2]}

# Error probability of primality test
ERROR=${4:-0.0}

mkdir -p $OUT_DIR
for ((min_value = $start; min_value < $stop; min_value = $min_value * $step))
do
  max_value=$(($min_value * $step))
  factor_dir=$"${OUT_DIR}/factor_${min_value}-${max_value}"
  mkdir -p $factor_dir

  command="python3 -m gen_factor_sat random"
  options="${max_value} --min-value ${min_value} --error ${ERROR} -o ${factor_dir}"

  total=$(($num_rand + $num_prime + $num_comp))
  for ((i = 0; i < $total; i++))
  do
    if ((i < $num_rand)); then
      num_type=""
    elif ((i < $num_rand + $num_prime)); then
      num_type="--prime"
    else
      num_type="--no-prime"
    fi
    eval $"${command} ${options} ${num_type}"
  done
done

