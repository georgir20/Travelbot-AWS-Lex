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
import io



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


def main_calc_destination_station_code(destination_station_name):
# use city from user input and query table in athena database
	client = boto3.client('athena')

	query_string= "SELECT DISTINCT current_station_code FROM trains_in_india WHERE current_station_name ='" + destination_station_name +"'"
	DATABASE_NAME = 'awt_voicebot_india'
	output_dir = 's3://awt-voicebot-output-destination-code'

	query_id = client.start_query_execution(
			QueryString = query_string,
			QueryExecutionContext = {
				'Database': DATABASE_NAME
			},
			ResultConfiguration = {
				'OutputLocation': output_dir
			}
		)['QueryExecutionId']
	
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
	s3 = boto3.client('s3')
	
	csvio = io.StringIO()
	writer = csv.writer(csvio)
	writer.writerow(['query_id'])
	writer.writerow([query_id])

	
	s3.put_object(Body=csvio.getvalue(), ContentType='text/csv', Bucket='awt-voicebot-output-destination-metadata', Key='destination_metadata.csv')
	csvio.close()
	
	return 'Ok we have set ' + destination_station_name + ' as your destination station. Do you now want to look up a station that you can enter for your start to make it to the hotel? If yes please enter "start".'
		
def return_StationCode(intent_request):
	destination_station_name = intent_request['currentIntent']['slots']['destination_station_name']
	source = intent_request['invocationSource']
	if source == 'DialogCodeHook':
		# Perform basic validation on the supplied input slots.
		slots = intent_request['currentIntent']['slots']
	return close(
		#output_session_attributes,
		'Fulfilled',
		{
			'contentType': 'PlainText',
			'content': main_calc_destination_station_code(destination_station_name) 
			
		}
	
	)	


""" --- Intents --- """
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch intentName={}'.format(intent_request['currentIntent']['name']))
    intent_name='SetDestinationStation'
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'SetDestinationStation':
        return return_StationCode(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def lambda_handler(event, context):
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))
	return dispatch(event)