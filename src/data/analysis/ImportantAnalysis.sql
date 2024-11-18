WITH distinct_test_dates AS (
    SELECT COUNT(DISTINCT "TestDate") AS total_test_dates
    FROM co_integration_test
),
valid_assets AS (
    SELECT cit."Asset 1", cit."Asset 2"
    FROM co_integration_test AS cit
    WHERE cit."Checked" = 'Yes'
      AND cit."ADF p-Value" < '0.05'
    GROUP BY cit."Asset 1", cit."Asset 2"
    HAVING COUNT(DISTINCT cit."TestDate") = (SELECT total_test_dates FROM distinct_test_dates)
)
SELECT cit."Asset 1" as "Asset 1",
       yf1.industry as "Asset 1 Industry",
       yf1.sector as "Asset 1 Sector",
       yf1.longName as "Asset 1 Long Name",
       cit."Asset 2" as "Asset 2",
       yf2.industry as "Asset 2 Industry",
       yf2.sector as "Asset 2 Sector",
       yf2.longName as "Asset 2 Long Name",
       cit."ADF p-Value",
       cit."TestDate"
FROM co_integration_test AS cit
JOIN valid_assets va
  ON cit."Asset 1" = va."Asset 1" AND cit."Asset 2" = va."Asset 2"
JOIN yahoo_finance_info AS yf1
  ON cit."Asset 1" = yf1.symbol
JOIN yahoo_finance_info AS yf2
  ON cit."Asset 2" = yf2.symbol
WHERE cit."Checked" = 'Yes'
  AND cit."ADF p-Value" < '0.05'
  AND yf1.industry = yf2.industry
ORDER BY cit."ADF p-Value" DESC
limit 10;