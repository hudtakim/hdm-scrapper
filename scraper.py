# scraper.py

from google_play_scraper import Sort, reviews
import pandas as pd
import numpy as np

def scrape_reviews(app_id, lang='id', country='id', count=10, score_filter=None, save_csv=False, filename='scrapped_data.csv'):
    result, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.MOST_RELEVANT,
        count=count,
        filter_score_with=score_filter
    )

    df = pd.DataFrame(np.array(result), columns=['review'])
    df = df.join(pd.DataFrame(df.pop('review').tolist()))
    df = df[['userName', 'score', 'at', 'content']]
    df = df.sort_values(by='at', ascending=False)

    if save_csv:
        df.to_csv(filename, index=False)

    return df
