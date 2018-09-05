#!/usr/bin/env bash

NUMBER_OF_PROPS=$(grep 'AC  GenProp' testing/test_constants/test_genome_properties.txt | wc -l | tr -d ' ')
NUMBER_OF_PROPS_PARSED=$(./test_parse_genome_properties_file.py -i testing/test_constants/test_genome_properties.txt | grep -o '^[1-9]* ')

if [ ${NUMBER_OF_PROPS} == ${NUMBER_OF_PROPS_PARSED} ];then
  echo "The correct number of genome properties were parsed.";
  exit 0
else
  echo "An incorrect number of genome properties were parsed.";
  exit 1
fi