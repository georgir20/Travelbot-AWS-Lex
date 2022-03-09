CREATE EXTERNAL TABLE IF NOT EXISTS trains_in_india (
`train_no` int,
`train_name` string,
`seq` int,
`current_station_code` string,
`current_station_name` string,
`current_station_location` string,
`current_station_district` string,
`current_station_state` string,
`arrival_time` int,
`departure_time` int,
`distance` int,
`source_station_code` string,
`source_station_name` string,
`source_station_location` string,
`source_station_district` string,
`source_station_state` string,
`destination_station_code` string,
`destination_station_name` string,
`destination_station_location` string,
`destination_station_district` string,
`destination_station_state` string
  ) 
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ';'
  LINES TERMINATED BY '\n'
  LOCATION 's3://awt-voicebot/data/india_trains';
  
  
  
  
  
  
 