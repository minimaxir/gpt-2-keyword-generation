# Keyword Generation Example

Here is an example using Reddit data, utilizing the Top 10 most-upvoted posts for the Top 100 Subreddits in February 2019 in `top_reddit_posts.csv`. *(CW: Sexual Language)*

First, install the dependencies + the pretrained spaCy model:

```shell
pip3 install requirements.txt
```

The input is the `title` of the Reddit post and the `subreddit` of the Reddit post as the category.

```python
from keyword_encode import encode_keywords
import ray

ray.init(object_store_memory=100 * 1000000,
         redis_max_memory=100 * 1000000)

encode_keywords(csv_path='example/top_reddit_posts.csv',
                out_path='example/top_reddit_posts_encoded.txt',
                category_field='subreddit',
                title_field='title',
                keyword_gen='title')        
```

If you are generating texts (e.g. with gpt-2-simple), you'll need to manually reformat the text for it to serve as a prefix. The /r/legaladvice example was made using the command on a GPU:

```shell
gpt_2_simple generate --temperature 0.7 --top_k 40 --nsamples 100 --batch_size 25 --length 200 --prefix "<|startoftext|>~\`legaladvice~^dog cat tree sue~@" --truncate "<|endoftext|>" --include_prefix False --nfiles 1 --sample_delim ''
```

Or if using the Python interface to gpt-2-simple:

```python
gpt2.generate(sess,
              temperature=0.7,
              top_k=40,
              nsamples=100,
              batch_size=25,
              length=200,
              prefix="<|startoftext|>~`legaladvice~^dog cat tree sue~@",
              truncate="<|endoftext|>",
              include_prefix=False,
              sample_delim=''
              )
```

NB: if using the CLI, you'll have to escape the backquote as above. For keywords with spaces, delimit them with a `-`.

## Reddit BigQuery

This BigQuery reproduces `top_reddit_posts.csv`.

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
