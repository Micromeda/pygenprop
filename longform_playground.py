# coding: utf-8

# In[24]:


from modules.genome_properties_longform_file_parser import parse_genome_property_longform_file
from modules.genome_properties_flat_file_parser import parse_genome_property_file
from modules.genome_properties_results import GenomePropertiesResults

# In[25]:


with open('testing/test_constants/genomeProperties.txt') as genome_property_file:
    properties_tree = parse_genome_property_file(genome_property_file)

# In[26]:


with open('testing/test_constants/LONGFORM_REPORT__C_chlorochromatii_CaD3.txt') as long_form_one:
    with open('testing/test_constants/LONGFORM_REPORT_GENOME_PROPERTIES_C_luteolum_DSM_273.txt') as long_form_two:
        long_form_one_assignments = parse_genome_property_longform_file(long_form_one)
        long_form_two_assignments = parse_genome_property_longform_file(long_form_two)

# In[33]:

genome_properties_results = GenomePropertiesResults(properties_tree, long_form_one_assignments,
                                                    long_form_two_assignments)
