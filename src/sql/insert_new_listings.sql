WITH new_listings AS (
    SELECT lpl.id, lpl.property, lpl.transaction
    FROM {listing_input} lpl
    LEFT JOIN immo_data.{listing_table} lis ON lpl.id = lis.id
    WHERE lis.id is NULL 
)
INSERT INTO immo_data.{listing_table}
SELECT *
FROM new_listings; 