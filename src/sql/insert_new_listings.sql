WITH new_listings AS (
    SELECT lpl.id, lpl.property, lpl.transaction
    FROM listing_pl lpl
    LEFT JOIN immo_data.listings lis ON lpl.id = lis.id
    WHERE lis.id is NULL 
)
INSERT INTO immo_data.listings
SELECT *
FROM new_listings; 