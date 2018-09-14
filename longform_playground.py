
# coding: utf-8

# In[20]:


from modules.genome_properties_longform_file_parser import parse_genome_property_longform_file
from modules.genome_properties_flat_file_parser import parse_genome_property_file
from modules.genome_properties_results import assign_genome_properties
import json
import pandas as pd


# In[21]:


with open('testing/test_constants/genomeProperties.txt') as genome_property_file:
    properties_tree = parse_genome_property_file(genome_property_file)


# In[22]:


with open('testing/test_constants/LONGFORM_REPORT__C_chlorochromatii_CaD3.txt') as long_form_one:
    with open('testing/test_constants/LONGFORM_REPORT_GENOME_PROPERTIES_C_luteolum_DSM_273.txt') as long_form_two:
        long_form_one_assignments = parse_genome_property_longform_file(long_form_one)
        long_form_two_assignments = parse_genome_property_longform_file(long_form_two)


# In[23]:


long_form_one_assignments


# In[24]:


name = long_form_one_assignments.pop('name')


# In[25]:


print(name)


# In[26]:


property_assignments = {}
global_step_assignments = {}
for genome_property_id, assignment_data in long_form_one_assignments.items():
    if bool(assignment_data['partial']):
        result = 'PARTIAL'
    else:
        result = 'YES'

    property_assignments[genome_property_id] = result

    all_step_numbers = set(step.number for step in properties_tree[genome_property_id].steps)
    supported_step_numbers = set(assignment_data['supported_steps'])
    unsupported_steps_numbers = all_step_numbers - supported_step_numbers

    current_genome_property_step_assignments = {}
    for step_number in supported_step_numbers:
        current_genome_property_step_assignments[step_number] = True

    for step_number in unsupported_steps_numbers:
        current_genome_property_step_assignments[step_number] = False

    global_step_assignments[genome_property_id] = current_genome_property_step_assignments

# In[27]:

root = properties_tree.root
genome_property_id = root.id

genome_property_result, new_genome_property_assignments, new_step_assignments = assign_genome_properties(properties_tree,
                                                                                                         property_assignments,
                                                                                                         global_step_assignments,
                                                                                                         genome_property_id)

