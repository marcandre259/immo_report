/*
The 0 argument is the desired name of the listing table
The 1 argument is the name of the polars dataframe containting the scraped listing data. 
*/
CREATE TABLE immo_data.{listing_table} AS 
SELECT lpl.id, lpl.property, lpl.transaction
FROM {listing_input} lpl