WITH new_listings AS (
    SELECT lpl.id, lpl.property, lpl.transaction, lis.id AS id_orig
    FROM {listing_input} lpl
    LEFT JOIN immo_data.{listing_table} lis ON lpl.id = lis.id
)
INSERT INTO immo_data.{listing_table}
SELECT nli.id, nli.property, nli.transaction
FROM new_listings nli
WHERE nli.id_orig is NULL; 