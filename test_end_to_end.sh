#!/usr/bin/env bash
set -euo pipefail

NUMBER_OF_PROPS=$(grep 'AC  GenProp' testing/test_constants/test_genome_properties.txt | wc -l | tr -d ' ')
NUMBER_OF_PROPS_PARSED=$(./test_parse_genome_properties_file.py  -i ./pygenprop/testing/test_constants/test_genome_properties.txt | grep -o '^[1-9]*')

echo "Number of GREPed genome properties: ${NUMBER_OF_PROPS}"
echo "Number of parsed genome properties: ${NUMBER_OF_PROPS_PARSED}"

if [[ ${NUMBER_OF_PROPS} == ${NUMBER_OF_PROPS_PARSED} ]];
then
  echo "The correct number of genome properties were parsed.";
  exit 0
else
  echo "An incorrect number of genome properties were parsed.";
  exit 1
fi