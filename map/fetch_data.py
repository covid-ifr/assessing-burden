import csv
import urllib2

study_index = []
study_prevalence = []


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
        else:
            print "Error finding a matching row"
            

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
clean_study_index(study_index,["map_x","map_y"])
fetch_study_total_seroprevalence()

match_data(study_index,study_prevalence,'location_id',['mean'])
save_data(study_index)

    
    