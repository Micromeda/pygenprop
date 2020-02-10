#!/usr/bin/env bash
set -euo pipefail

extract_info_stats() {
# Converts human readable output from pygenprop info into a column of numbers.
    grep -v 'The Micromeda file contains the following:' | grep ":" | cut -d':' -f 2 | awk '{$1=$1};1'
}

RESULT_JOINED=$(pygenprop info -i joined_cloroflexi_data.micro | extract_info_stats)
RESULT_LUT=$(pygenprop info -i luteolum_data.micro | extract_info_stats)
RESULT_CHL=$(pygenprop info -i chloromatii_data.micro | extract_info_stats)
RESULT_MERGED=$(pygenprop info -i merged_cholorflexi_data.micro | extract_info_stats)

if [[ ${RESULT_JOINED} == ${RESULT_MERGED} ]]
then
    echo "Good, joined and merged results are the same."
else
    echo "Bad, joined and merged results are not the same."
    exit 1
fi

sum_rows() {
# Sums two columns of numbers created by extract_info_stats().
    awk '{sum=0; for (i=1; i<=NF; i++) { sum+= $i } print sum}'
}

# Sums the numbers from RESULT_LUT and RESULT_CHL.
RESULT_TOTALED_LUT_CHL=$(paste <(echo "$RESULT_LUT") <(echo "$RESULT_CHL") | sum_rows)

if [[ ${RESULT_TOTALED_LUT_CHL} == ${RESULT_MERGED} ]]
then
    echo "Good, separated and merged results are the same."
else
    echo "Bad, separated and merged results are not the same."
    exit 1
fi