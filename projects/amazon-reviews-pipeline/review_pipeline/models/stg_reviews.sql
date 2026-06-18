{{ config(
    materialized='incremental',
    unique_key='id',
    on_schema_change='fail'
) }}

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
    loaded_at,
    CASE
        WHEN score >= 4 THEN 'POSITIVE'
        WHEN score <= 2 THEN 'NEGATIVE'
        ELSE 'NEUTRAL'
    END AS rating_sentiment
FROM {{ source('amazon_reviews', 'raw_reviews') }}

{% if is_incremental() %}
    WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
{% endif %}