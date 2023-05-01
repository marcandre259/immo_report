CREATE TABLE (
id UBIGINT NULL,
property STRUCT("type" VARCHAR, subtype VARCHAR, "location" STRUCT(locality VARCHAR, "postalCode" BIGINT)) NULL,
transaction STRUCT("type" VARCHAR)
);