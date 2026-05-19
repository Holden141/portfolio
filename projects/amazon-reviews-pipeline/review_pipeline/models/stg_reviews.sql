SELECT
    id,
    productid,
    userid,
    profilename,
    helpfulnessnumerator,
    helpfulnessdenominator,
    score,
    time,
    summary,
    text,
    CASE
        WHEN score >= 4 THEN 'POSITIVE'
        WHEN score <= 2 THEN 'NEGATIVE'
        ELSE 'NEUTRAL'
    END AS rating_sentiment
FROM {{ source('amazon_reviews', 'raw_reviews') }}
WHERE
    text IS NOT NULL
    AND text != ''