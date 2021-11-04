import csv
import urllib2

study_index = []
study_prevalence = []
study_ifr = []
study_link = []
risk_info = []


'''
Function fetching necessary data from the file study_index.csv
'''
def fetch_study_info():
    global study_index
    url = 'https://raw.githubusercontent.com/covid-ifr/assessing-burden/main/input_data/study_index.csv'
    response = urllib2.urlopen(url)
    #cr = csv.DictReader(response)

    #data_to_add = ['location_id','study_info','country','location_label','start_date','end_date']

    study_index = list(csv.DictReader(response))
    #print study_index['location_id']

    #for row in cr:

        #study_index.append([row['location_id'],row['study_info'],row['country'],row['location_label'],row['start_date'],row['end_date'],])


'''
Function fetching necessary data from the file total_seroprevalence.csv
'''
def fetch_study_total_seroprevalence():
    global study_prevalence
    url = 'https://raw.githubusercontent.com/covid-ifr/assessing-burden/main/model_output/total_seroprevalence.csv'
    response = urllib2.urlopen(url)
    study_prevalence = list(csv.DictReader(response))

    #cr = csv.DictReader(response)

    #for row in cr:
    #    study_prevalence.append([row['location_id'],row['mean']])


'''
Function fetching the studies' links
This function needs to do some extra parsing. The links to the studies are not always in the same column.
We thus need to find the location of all links for each study (if available)
'''
def fetch_study_link():
    global study_link
    url = 'https://raw.githubusercontent.com/covid-ifr/assessing-burden/main/appendix_material/included_study_info.csv'
    response = urllib2.urlopen(url)
    reader = csv.reader(response, delimiter = ',')
    for row in reader:
        location_id = row[0]
        source = row[4]
        link_one = ''
        link_two = ''
        for i in range(5, 11):
            col = row[i]
            #print 'col = '+str(col)
            if link_one == '' or link_two =='':
                if 'http' in col:
                    if link_one == '':
                        link_one = col
                    elif link_two == '':
                        link_two = col
        dict_elem = {'location_id':location_id,'source':source,'link_one':link_one,'link_two':link_two}
        study_link.append(dict_elem)


'''
Function fetching necessary data from the file risk_of_bias_assessments.csv
'''
def fetch_bias_risk_info():
    global risk_info 
    url = 'https://raw.githubusercontent.com/covid-ifr/assessing-burden/main/appendix_material/risk_of_bias_assessments.csv'
    response = urllib2.urlopen(url)
    risk_info = list(csv.DictReader(response))


'''
Function fetching necessary data from the file population_ifr.csv
Does some extra processing of the IFR values (CIs and means) to make it a percentage
'''
def fetch_study_total_ifr():
    global study_ifr
    url = 'https://raw.githubusercontent.com/covid-ifr/assessing-burden/main/model_output/population_ifr.csv'
    response = urllib2.urlopen(url)
    study_ifr = list(csv.DictReader(response))

    for row in study_ifr:
        row["IFR_mean"] = round((float(row["IFR_mean"])),9)
        row["IFR_p025"] = round((float(row["IFR_p025"])),9)
        row["IFR_p975"] = round((float(row["IFR_p975"])),9)

'''
Function to remove specific keys in a list of dict
@param1 input, the list
@param2 list_of_keys_to_remove, the keys to remove
'''
def clean_study_index(input, list_of_keys_to_remove):
    for row in input:
        for k in list_of_keys_to_remove:
            del row[k]


'''
Function that fetches the row in a list of dict that contains a specific (supposedly unique) value
@param1 field_name, the name of the field containing the unique value
@param2 field_value, the value of that specific field that we are looking for
@param3 input, the list of dict
@return the row if found, -1 otherwise
'''
def get_matching_row(field_name,field_value,input):
    for row in input:
        if(row[field_name] == field_value):
            return row
    return -1

'''
Function that matches the data from two input arrays, based on a specific field
@param1 input1, the first array to match data from
@param2 input2, the second array to match data from
@param3 field, the field to use to match data
@param4 fields_to_add, a list containing the fields to add to input1 from input2
'''
def match_data(input1, input2, field, fields_to_add):
    for row in input1:
        field_value = row[field]
        corresponding_row = get_matching_row(field,field_value,input2)
        #print "field_value = "+str(field_value)
        #print str(corresponding_row[fields_to_add[0]]) + " ----- " + str(corresponding_row[field])
        if corresponding_row!= -1:
            for f in fields_to_add:
                row[f] = corresponding_row[f]
        '''else:
            print "Error finding a matching row for "+str(field_value)'''
            

'''
Function that saves the data we have found into a csv file
@param1 input, the data to save
@return none
'''
def save_data(input):
    with open('map_data.csv', 'w') as csv_file:
        fieldnames = list(input[0].keys())
        writer = csv.DictWriter(csv_file,fieldnames=fieldnames)
        writer.writeheader()
        for row in input:
            writer.writerow(row)




fetch_study_info()
clean_study_index(study_index,["map_x","map_y","pop_location_id"])
fetch_study_total_seroprevalence()
fetch_study_total_ifr()
fetch_study_link()
fetch_bias_risk_info()

match_data(study_index,study_prevalence,'location_id',['mean','p025','p975'])
match_data(study_index,study_ifr,'location_id',['IFR_mean','IFR_p025','IFR_p975'])
match_data(study_index,study_link,'location_id',['source','link_one','link_two'])
match_data(study_index,risk_info,'location_id',['non_response_risk','seroreversion_risk','death_undercount_risk'])
save_data(study_index)

    
    