import json
import csv
import boto3
import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
from math import floor

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def close(fulfillment_state, message):				
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response


def main_calc_find_direct_connection():
# open metadata  for arrival and destination to grab query_ids which are names of csv files with station codes
    s3=boto3.client('s3')
    filename_hm = "hotel_arrival_metadata.csv"
    fileObj_hm = s3.get_object(Bucket = 'awt-voicebot-output-hotel-metadata', Key=filename_hm)
    rows_hm = fileObj_hm['Body'].read().decode('utf-8').splitlines()
    csvreader = csv.reader(rows_hm, dialect=csv.excel)
    array_hm = []
    headers = next(csvreader)
    for i in csvreader:
    	array_hm.append(i)
    hotel_query_id = array_hm[0] 
    
    
    filename_hd = hotel_query_id[0] + ".csv"
    fileObj_hd = s3.get_object(Bucket = 'awt-voicebot-output', Key=filename_hd)
    rows_hd = fileObj_hd['Body'].read().decode('utf-8').splitlines()
    csvreader = csv.reader(rows_hd, dialect=csv.excel)
    array_hd = []
    
    headers = next(csvreader)
    for i in csvreader:
    	array_hd.append(i)
    hotel_address = array_hd[0]
    
    
    
    
    print("Hotel address: " + hotel_address[0])
    
# # now query the hotel table with the hotel name to get the state, the city and the area
    client = boto3.client('athena')

    query_string= "SELECT DISTINCT city, area, state, property_name FROM hotels_in_india WHERE property_address ='" + hotel_address[0] + "'"
    DATABASE_NAME = 'awt_voicebot_india'
    output_dir = 's3://awt-voicebot-output-hotel-train'

    query_id = client.start_query_execution(
    		QueryString = query_string,
    		QueryExecutionContext = {
    			'Database': DATABASE_NAME
    		},
    		ResultConfiguration = {
    			'OutputLocation': output_dir
    		}
    	)['QueryExecutionId']
    query_id1=query_id
    ##-----------------------don't change --------------------------------------------	
    query_status = None
    while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
    	query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
    	if query_status == 'FAILED' or query_status == 'CANCELLED':
    		raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
    	time.sleep(1)
    results_paginator = client.get_paginator('get_query_results')
    results_iter = results_paginator.paginate(
    	QueryExecutionId=query_id,
    	PaginationConfig={
    	'PageSize': 1000
    	}
    )
    results = []
    data_list = []
    for results_page in results_iter:
    	for row in results_page['ResultSet']['Rows']:
    		data_list.append(row['Data'])
    # --------------------------don't change the above -------------------------------------			

#   open new csv query for addtional hotel info and query train dataset to find relevant stations near the hotel
# 	s3=boto3.client('s3')
    filename_ht = query_id1 + ".csv"
    fileObj_ht = s3.get_object(Bucket = 'awt-voicebot-output-hotel-train', Key=filename_ht)
    rows_ht = fileObj_ht['Body'].read().decode('utf-8').splitlines()
    csvreader = csv.reader(rows_ht, dialect=csv.excel)
    array_ht = []
    headers = next(csvreader)
    for i in csvreader:
    		array_ht.append(i)
    print(array_ht)
# assign values from hotel query to variables that are used to query train data set
    destination_station_location = str(array_ht[0][0])
    destination_station_district = str(array_ht[0][1])
    destination_station_state = str(array_ht[0][2])
    hotel_name = array_ht[0][3]
    print('Hotel_city: ' + destination_station_location)
    print('Hotel_district: ' + destination_station_district)
    print('Hotel_state: ' + destination_station_state)

# #  Execute Query for connection information of arrival station	
    client = boto3.client('athena')
    query_string = "SELECT DISTINCT current_station_name FROM trains_in_india WHERE current_station_location ='" + destination_station_location + "'"
    DATABASE_NAME = 'awt_voicebot_india'
    output_dir = 's3://awt-voicebot-output-destination-hotel'	
    		
    query_id = client.start_query_execution(
    		QueryString = query_string,
    		QueryExecutionContext = {
    		'Database': DATABASE_NAME
    		},
    		ResultConfiguration = {
    		'OutputLocation': output_dir
    		}
    	)['QueryExecutionId']
    query_id2=query_id
#-----------------------don't change --------------------------------------------	
    query_status = None
    while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
    	query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
    	if query_status == 'FAILED' or query_status == 'CANCELLED':
    		raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
    	time.sleep(1)
    results_paginator = client.get_paginator('get_query_results')
    results_iter = results_paginator.paginate(
    	QueryExecutionId=query_id,
    	PaginationConfig={
    	'PageSize': 1000
    	}
    )
    results = []
    data_list = []
    for results_page in results_iter:
    	for row in results_page['ResultSet']['Rows']:
    		data_list.append(row['Data'])

# open csv again and read train stations for destination near hotel city				
    s3=boto3.client('s3')
    filename_htl = query_id2 + ".csv"
    fileObj_htl = s3.get_object(Bucket = 'awt-voicebot-output-destination-hotel', Key=filename_htl)
    rows_htl = fileObj_htl['Body'].read().decode('utf-8').splitlines()
    
    csvreader = csv.reader(rows_htl, dialect=csv.excel)
    array_htl = []
    headers = next(csvreader)
    for i in csvreader:
    	array_htl.append(i)
    
    if array_htl :
        return 'We found the following stations in the city of your hotel.' + 'The stations are: {}.'.format(array_htl) + ' Do you want to set one of those stations as your destination station?'
 # Execute Query for connection information with train station in the same district as hotel    
    else: 
        client = boto3.client('athena')
        query_string = "SELECT DISTINCT current_station_name FROM trains_in_india WHERE current_station_location ='" + destination_station_district + "'"
        DATABASE_NAME = 'awt_voicebot_india'
        output_dir = 's3://awt-voicebot-output-destination-hotel'	
        	
        query_id = client.start_query_execution(
        		QueryString = query_string,
        		QueryExecutionContext = {
        		'Database': DATABASE_NAME
        		},
        		ResultConfiguration = {
        		'OutputLocation': output_dir
        		}
        	)['QueryExecutionId']
        query_id3=query_id
        #-----------------------don't change --------------------------------------------	
        query_status = None
        while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
        	query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
        	if query_status == 'FAILED' or query_status == 'CANCELLED':
        		raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
        	time.sleep(1)
        results_paginator = client.get_paginator('get_query_results')
        results_iter = results_paginator.paginate(
        	QueryExecutionId=query_id,
        	PaginationConfig={
        	'PageSize': 1000
        	}
        )
        results = []
        data_list = []
        for results_page in results_iter:
        	for row in results_page['ResultSet']['Rows']:
        		data_list.append(row['Data'])
        
        # open csv again and read train stations for destination near hotel city			
        s3=boto3.client('s3')
        filename_htd = query_id3 + ".csv"
        fileObj_htd = s3.get_object(Bucket = 'awt-voicebot-output-destination-hotel', Key=filename_htd)
        rows_htd = fileObj_htd['Body'].read().decode('utf-8').splitlines()
        
        csvreader = csv.reader(rows_htd, dialect=csv.excel)
        array_htd = []
        headers = next(csvreader)
        for i in csvreader:
        	array_htd.append(i)
        
        if array_htd :	
            return 'We found the following stations in the district of your hotel: ' + hotel_address[0] +' Do you want to set one of those stations as your destination station?'
    #  Execute Query for connection information with train station in the same state as hotel
        else: 
            client = boto3.client('athena')
            query_string = "SELECT DISTINCT current_station_name FROM trains_in_india WHERE current_station_location ='" + destination_station_state + "'"
            DATABASE_NAME = 'awt_voicebot_india'
            output_dir = 's3://awt-voicebot-output-destination-hotel'	
            	
            query_id = client.start_query_execution(
            		QueryString = query_string,
            		QueryExecutionContext = {
            		'Database': DATABASE_NAME
            		},
            		ResultConfiguration = {
            		'OutputLocation': output_dir
            		}
            	)['QueryExecutionId']
            query_id4=query_id
            #-----------------------don't change --------------------------------------------	
            query_status = None
            while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
            	query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
            	if query_status == 'FAILED' or query_status == 'CANCELLED':
            		raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
            	time.sleep(1)
            results_paginator = client.get_paginator('get_query_results')
            results_iter = results_paginator.paginate(
            	QueryExecutionId=query_id,
            	PaginationConfig={
            	'PageSize': 1000
            	}
            )
            results = []
            data_list = []
            for results_page in results_iter:
            	for row in results_page['ResultSet']['Rows']:
            		data_list.append(row['Data'])
            
            # open csv again and read train stations for destination near hotel city			
            s3=boto3.client('s3')
            filename_hts = query_id4 + ".csv"
            fileObj_hts = s3.get_object(Bucket = 'awt-voicebot-output-destination-hotel', Key=filename_hts)
            rows_hts = fileObj_hts['Body'].read().decode('utf-8').splitlines()
            
            csvreader = csv.reader(rows_hts, dialect=csv.excel)
            array_hts = []
            headers = next(csvreader)
            for i in csvreader:
            	array_hts.append(i)
            
            if array_hts :	
                return 'We found the following stations in the state of your hotel: ' + hotel_address[0] +' Do you want to set one of those stations as your destination station?'
            
            else :
                return 'We could not find any train stations close to your hotel.'

def return_StationName(intent_request):
	#destination_station_state = intent_request['currentIntent']['slots']['destination_station_state']
	source = intent_request['invocationSource']
	if source == 'DialogCodeHook':
		# Perform basic validation on the supplied input slots.
		slots = intent_request['currentIntent']['slots']
	return close(
		#output_session_attributes,
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': main_calc_find_direct_connection() 
			
		}
		)



""" --- Intents --- """
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch intentName={}'.format(intent_request['currentIntent']['name']))
    intent_name='GetDestinationStationHotel'
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'GetDestinationStationHotel':
        return return_StationName(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def lambda_handler(event, context):
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)