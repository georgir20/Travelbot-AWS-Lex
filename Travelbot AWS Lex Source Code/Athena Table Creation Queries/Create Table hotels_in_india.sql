CREATE EXTERNAL TABLE IF NOT EXISTS hotels_in_india (
  `area` string,
  `city` string,
  `highlight_value` string,
  `hotel_overview` string,
  `hotel_star_rating` int,
  `latitude` int,
  `longitude` int,
  `mmt_review_count` int,
  `mmt_review_rating` string,
  `mmt_review_score` int,
  `property_address` string,
  `property_id` string,
  `property_name` string,
  `room_types` string,
  `site_review_rating` int,
  `state` string,
  `traveller_rating` string,
  `uniq_id` string
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ';'
  LINES TERMINATED BY '\n'
  LOCATION 's3://awt-voicebot/data/india_hotels';