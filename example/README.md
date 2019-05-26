# Keyword Generation Example

Here is an example using Reddit data, utilizing the Top 10 posts for the Top 100 Subreddits in `top_reddit_posts.csv`. **(CW: Sexual Language)**

The input is the `title` of the Reddit post and the `subreddit` of the Reddit post as the category.

```python
from keyword_encode import encode_keywords

encode_keywords(csv_path='example/top_reddit_posts.csv',
                out_path='example/top_reddit_posts_encoded.txt',
                category_field='subreddit',
                title_field='title',
                keyword_gen='title')
```

## Reddit BigQuery

```sql
#standardSQL
WITH
  subreddits AS (
  SELECT
    subreddit
  FROM
    `fh-bigquery.reddit_posts.2019_02`
  WHERE
    score >= 5
    AND subreddit NOT IN ("me_irl",
      "2meirl4meirl",
      "anime_irl",
      "furry_irl",
      "cursedimages",
      "meirl",
      "hmmm")
  GROUP BY
    subreddit
  ORDER BY
    APPROX_COUNT_DISTINCT(author) DESC
  LIMIT
    100 )
    

SELECT
  subreddit,
  REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(title, '&amp;', '&'), '&lt;', '<'), '&gt;', '>'), '�', '') as title
FROM (
  SELECT
    subreddit,
    title,
    ROW_NUMBER() OVER (PARTITION BY subreddit ORDER BY score DESC) AS score_rank
  FROM
    `fh-bigquery.reddit_posts.2019_02`
  WHERE
    subreddit IN (SELECT subreddit FROM subreddits) )
WHERE
  score_rank <= 10
ORDER BY subreddit
```