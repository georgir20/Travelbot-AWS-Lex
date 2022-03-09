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
	filename_am = "arrival_metadata.csv"
	fileObj_am = s3.get_object(Bucket = 'awt-voicebot-output-arrival-metadata', Key=filename_am)
	rows_am = fileObj_am['Body'].read().decode('utf-8').splitlines()
	csvreader = csv.reader(rows_am, dialect=csv.excel)
	array_am = []
	headers = next(csvreader)
	for i in csvreader:
		array_am.append(i)
	arrival_query_id = array_am[0] 
	
	#s3=boto3.client('s3')
	filename_dm = "destination_metadata.csv"
	fileObj_dm = s3.get_object(Bucket = 'awt-voicebot-output-destination-metadata', Key=filename_dm)
	rows_dm = fileObj_dm['Body'].read().decode('utf-8').splitlines()
	csvreader = csv.reader(rows_dm, dialect=csv.excel)
	array_dm = []

	headers = next(csvreader)
	for i in csvreader:
		array_dm.append(i)
	destination_query_id = array_dm[0]
	
	print("arrival_query_id:"+ arrival_query_id[0])
	
	print("destination_query_id:"+ destination_query_id[0])
#open csv files with station codes for arrival and destination

	s3=boto3.client('s3')
	filename_a = arrival_query_id[0] + ".csv"
	fileObj_a = s3.get_object(Bucket = 'awt-voicebot-output-arrival-code', Key=filename_a)
	rows_a = fileObj_a['Body'].read().decode('utf-8').splitlines()
	csvreader = csv.reader(rows_a, dialect=csv.excel)
	array_a = []
	
	headers = next(csvreader)
	for i in csvreader:
		array_a.append(i)
	arrival_code = array_a[0]
	
	s3=boto3.client('s3')
	filename_d = destination_query_id[0] + ".csv"
	fileObj_d = s3.get_object(Bucket = 'awt-voicebot-output-destination-code', Key=filename_d)
	rows_d = fileObj_d['Body'].read().decode('utf-8').splitlines()
	csvreader = csv.reader(rows_d, dialect=csv.excel)
	array_d = []
	
	headers = next(csvreader)
	for i in csvreader:
		array_d.append(i)
	destination_code = array_d[0]
	
	print("Arrival code: " + arrival_code[0])
	print("Destination Code: " + destination_code[0])
	print("Arrival code: " + arrival_code[0])
	print("Destination Code: " + destination_code[0])
	
## now query the database with the arrival_code and departure_code to find the train number of a direct connection train
	client = boto3.client('athena')
	
	query_string= "SELECT DISTINCT train_no FROM trains_in_india WHERE current_station_code ='" + arrival_code[0] + "' INTERSECT SELECT DISTINCT train_no FROM trains_in_india WHERE current_station_code ='" + destination_code[0] + "'"
	DATABASE_NAME = 'awt_voicebot_india'
	output_dir = 's3://awt-voicebot-output-direct-connection'

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
# --------------------------don't change the above -------------------------------------			



	
# open new csv query result and read into lex bot
	s3=boto3.client('s3')
	filename_dc = query_id1 + ".csv"
	fileObj_dc = s3.get_object(Bucket = 'awt-voicebot-output-direct-connection', Key=filename_dc)
	rows_dc = fileObj_dc['Body'].read().decode('utf-8').splitlines()
	
	csvreader = csv.reader(rows_dc, dialect=csv.excel)
	array_dc = []
	headers = next(csvreader)
	for i in csvreader:
		array_dc.append(i)
	
	print(array_dc)
# Execute Query for connection information of arrival station (if there exists a direct connection)
	if array_dc :

		result_train1=array_dc[0]
		print('Train number found' + result_train1[0])
		print('Arrival code after train_no found: ' +  arrival_code[0])
		print('Destination code after train_no found: ' + destination_code[0])
		client = boto3.client('athena')
		query_string = "SELECT train_no, current_station_code, current_station_name, seq, arrival_time, departure_time, destination_station_name FROM trains_in_india WHERE (current_station_code= '" + arrival_code[0] + "' AND train_no=" + result_train1[0] + ")"
		output_dir = 's3://awt-voicebot-output-direct-connection'	
			
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

# open csv again and read train connection data into proper table for arrival station
		
		s3=boto3.client('s3')
		filename_dcfa = query_id2 + ".csv"
		fileObj_dcfa = s3.get_object(Bucket = 'awt-voicebot-output-direct-connection', Key=filename_dcfa)
		rows_dcfa = fileObj_dcfa['Body'].read().decode('utf-8').splitlines()
		
		csvreader = csv.reader(rows_dcfa, dialect=csv.excel)
		array_dcfa = []
		headers = next(csvreader)
		for i in csvreader:
			array_dcfa.append(i)
		print('Connection Results for Arrival station: ')
		print(array_dcfa[0][1])
		train_number=array_dcfa[0][0]
		terminal_station=array_dcfa[0][6]
		arrival_station=array_dcfa[0][2]
		arrival_seq=int(array_dcfa[0][3])
		arrival_time=int(array_dcfa[0][4])

# Execute Query for connection information of destination station	
		client = boto3.client('athena')
		query_string = "SELECT train_no, current_station_code, current_station_name, seq, arrival_time, departure_time, destination_station_name FROM trains_in_india WHERE (current_station_code= '" + destination_code[0] + "' AND train_no=" + result_train1[0] + ")"
		DATABASE_NAME = 'awt_voicebot_india'
		output_dir = 's3://awt-voicebot-output-direct-connection'	
			
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

# open csv again and read train connection data into proper table for destination station				
		s3=boto3.client('s3')
		filename_dcfd = query_id3 + ".csv"
		fileObj_dcfd = s3.get_object(Bucket = 'awt-voicebot-output-direct-connection', Key=filename_dcfd)
		rows_dcfd = fileObj_dcfd['Body'].read().decode('utf-8').splitlines()
		
		csvreader = csv.reader(rows_dcfd, dialect=csv.excel)
		array_dcfd = []
		headers = next(csvreader)
		for i in csvreader:
			array_dcfd.append(i)
		print('Connection Results for destination station: ')
		train_number2=array_dcfd[0][0]
		destination_station=array_dcfd[0][2]
		destination_seq=int(array_dcfd[0][3])
		destination_time_init=int(array_dcfd[0][5])
		destination_time = 0
		ride_time = 0
		
		print('desintaion_time_init: ' + str(destination_time_init))
		print('Train Number: ' + train_number)
		print('Train Number2: '+ train_number2)
		print('Arrival Time: ' + str(arrival_time))
		print('Destination Time: ' + str(destination_time))
		
		if (destination_seq > arrival_seq):
			station_amount = destination_seq - arrival_seq
		else:
			station_amount = arrival_seq - destination_seq
		
		# C1-A
		if (destination_seq > arrival_seq and destination_time_init > arrival_time):
			ride_time = destination_time_init - arrival_time
			destination_time = destination_time_init ;
		#C1-B    
		if (destination_seq > arrival_seq and destination_time_init < arrival_time):
			ride_time = ((86400 - arrival_time) + destination_time_init)
			destination_time = destination_time_init;
		#C2-A    
		if (destination_seq < arrival_seq and destination_time_init < arrival_time):
			ride_time = arrival_time - destination_time_init
			destination_time = arrival_time + ride_time;

		#C2-B
		if (destination_seq < arrival_seq and destination_time_init > arrival_time):
			ride_time = (86400 - destination_time_init) + arrival_time
			destination_time= arrival_time + ride_time;		
		
		if (destination_time > 86400):
			if (destination_time > 172800) :
				destination_time = destination_time - 172800
			else:
				destination_time = destination_time - 86400
		
		
		#time converter from UNIX format (Athena) to HH:MM format to make it readable for the user
		def convert_seconds_to_timestamp(seconds):
		    minutes = floor(seconds/60)
		    hours = floor(minutes/60)
		    rest_minutes = int(minutes % 60)
		    if(hours < 10):
		        hours = '0' + str(hours)
		    if(rest_minutes < 10):
		       rest_minutes = '0' + str(rest_minutes)
		    return f'{hours}:{rest_minutes}'	
		
		arrival_time_normal = convert_seconds_to_timestamp(arrival_time)
		destination_time_normal = convert_seconds_to_timestamp(destination_time)
		ride_time_normal = convert_seconds_to_timestamp(ride_time)
		
		
		return 'We found a direct connection for you. Please go to ' + arrival_station + ' at ' + arrival_time_normal	+ ' o´clock and take the train ' + str(train_number) + ' which goes to ' + terminal_station + '.' + ' It will take you about ' + ride_time_normal + ' hours and you need to pass ' + str(station_amount) + ' stations to get to your destination station ' + destination_station + ' at: ' + destination_time_normal + ' o´clock.'

# The following code is the start of the implementation of an indirect connction functionality with a 1-time intersection
# start query process for indirect (1 intersection) connection 
# get all needed attributes of arrival and destination station
	else: 
		return 'Sorry we could not find a direct connection'
# get all needed attributes for arrival station		
# 		client = boto3.client('athena')
# 		query_string = "SELECT train_no, current_station_code, seq, arrival_time, current_station_name, destination_station_name FROM trains_in_india WHERE current_station_code='" + arrival_code[0] + "'"
# 		DATABASE_NAME = 'awt_voicebot_india'
# 		output_dir = 's3://awt-voicebot-output-indirect-connection'	
			
# 		query_id = client.start_query_execution(
# 				QueryString = query_string,
# 				QueryExecutionContext = {
# 				'Database': DATABASE_NAME
# 				},
# 				ResultConfiguration = {
# 				'OutputLocation': output_dir
# 				}
# 			)['QueryExecutionId']
# 		query_id2=query_id
# #-----------------------don't change --------------------------------------------	
# 		query_status = None
# 		while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
# 			query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
# 			if query_status == 'FAILED' or query_status == 'CANCELLED':
# 				raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
# 			time.sleep(1)
# 		results_paginator = client.get_paginator('get_query_results')
# 		results_iter = results_paginator.paginate(
# 			QueryExecutionId=query_id,
# 			PaginationConfig={
# 			'PageSize': 1000
# 			}
# 		)
# 		results = []
# 		data_list = []
# 		for results_page in results_iter:
# 			for row in results_page['ResultSet']['Rows']:
# 				data_list.append(row['Data'])

# # open csv again and read train connection data into proper table for arrival station
		
# 		s3=boto3.client('s3')
# 		filename_icav = query_id2 + ".csv"
# 		fileObj_icav = s3.get_object(Bucket = 'awt-voicebot-output-indirect-connection', Key=filename_icav)
# 		rows_icav = fileObj_icav['Body'].read().decode('utf-8').splitlines()
		
# 		csvreader = csv.reader(rows_icav, dialect=csv.excel)
# 		array_icav = []
# 		headers = next(csvreader)
# 		for i in csvreader:
# 			array_icav.append(i)
# 		print('Connection Results for Arrival station: ')

# 		a_s_train_no=array_icav[0][0]
# 		a_s_code=array_icav[0][1]
# 		a_s_seq=int(array_icav[0][2])
# 		a_s_arrival_time=int(array_icav[0][3])
# 		a_s_name=array_icav[0][4]
# 		a_destination_station_name=array_icav[0][5]
		
# 		print('	a_s_train_no: ' + str(a_s_train_no) + 'a_s_code: ' + a_s_code + 'a_s_seq: '+ str(a_s_seq) + 'a_s_arrival_time: ' + str(a_s_arrival_time) + 'a_s_name: ' + a_s_name + 'a_destination_station_name: ' + a_destination_station_name)


# # get all needed attributes for destination station	
# 		client = boto3.client('athena')
# 		query_string = "SELECT train_no, current_station_code, seq, arrival_time, current_station_name, destination_station_name FROM trains_in_india WHERE current_station_code='" + destination_code[0] + "'"
# 		DATABASE_NAME = 'awt_voicebot_india'
# 		output_dir = 's3://awt-voicebot-output-indirect-connection'	
			
# 		query_id = client.start_query_execution(
# 				QueryString = query_string,
# 				QueryExecutionContext = {
# 				'Database': DATABASE_NAME
# 				},
# 				ResultConfiguration = {
# 				'OutputLocation': output_dir
# 				}
# 			)['QueryExecutionId']
# 		query_id3=query_id
# #-----------------------don't change --------------------------------------------	
# 		query_status = None
# 		while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
# 			query_status = client.get_query_execution(QueryExecutionId=query_id)['QueryExecution']['Status']['State']
# 			if query_status == 'FAILED' or query_status == 'CANCELLED':
# 				raise Exception('Athena query with the string "{}" failed or was cancelled'.format(query_string))
# 			time.sleep(1)
# 		results_paginator = client.get_paginator('get_query_results')
# 		results_iter = results_paginator.paginate(
# 			QueryExecutionId=query_id,
# 			PaginationConfig={
# 			'PageSize': 1000
# 			}
# 		)
# 		results = []
# 		data_list = []
# 		for results_page in results_iter:
# 			for row in results_page['ResultSet']['Rows']:
# 				data_list.append(row['Data'])

# # open csv again and read train connection data into proper table for destination station
	
# 		s3=boto3.client('s3')
# 		filename_icdv = query_id3 + ".csv"
# 		fileObj_icdv = s3.get_object(Bucket = 'awt-voicebot-output-indirect-connection', Key=filename_icdv)
# 		rows_icdv = fileObj_icdv['Body'].read().decode('utf-8').splitlines()
		
# 		csvreader = csv.reader(rows_icdv, dialect=csv.excel)
# 		array_icdv = []
# 		headers = next(csvreader)
# 		for i in csvreader:
# 			array_icdv.append(i)
# 		print('Connection Results for Destination station: ')

# 		d_s_train_no=array_icdv[0][0]
# 		d_s_code=array_icdv[0][1]
# 		d_s_seq=int(array_icdv[0][2])
# 		d_s_arrival_time=int(array_icdv[0][3])
# 		d_s_name=array_icdv[0][4]
# 		d_destination_station_name=array_icdv[0][5]
		
# 		print('	d_s_train_no: ' + str(d_s_train_no) + ' d_s_code: ' + d_s_code + ' d_s_seq: '+ str(d_s_seq) + ' d_s_arrival_time: ' + str(d_s_arrival_time) + ' d_s_name: ' + d_s_name + ' d_destination_station_name: ' + d_destination_station_name)
# 		print('	a_s_train_no: ' + str(a_s_train_no) + ' a_s_code: ' + a_s_code + ' a_s_seq: '+ str(a_s_seq) + ' a_s_arrival_time: ' + str(a_s_arrival_time) + ' a_s_name: ' + a_s_name + ' a_destination_station_name: ' + a_destination_station_name)
		
		
		
		
		
		
		
		
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
    intent_name='FindDirectConnection'
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'FindDirectConnection':
        return return_StationName(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def lambda_handler(event, context):
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)