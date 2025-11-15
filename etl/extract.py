import io
from datetime import datetime

import pandas as pd
import requests

from configs import settings
from etl.utils import get_logger

logger = get_logger(__name__)


def fetch_coingecko(per_page=settings.COINGECKO_PER_PAGE, page=settings.COINGECKO_PAGE):
    """
    Calls CoinGecko API and returns a pandas DataFrame and an in-memory CSV string.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
    except Exception as e:
        logger.error(f"=== Error while requesting CoinGecko API: {e} ===")
        raise

    if resp.status_code != 200:
        logger.error(f"=== Connection Failed for Error Code {resp.status_code} ===")
        resp.raise_for_status()

    logger.info("=== Connection Succesful!, Getting Data!... ===")
    data = resp.json()
    logger.info("=== Data received! ===")

    df = pd.DataFrame(data)
    logger.info("=== Created Dataframe ===")

    # keep only the columns you used originally
    selected_cols = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "price_change_percentage_24h",
        "ath",
        "atl",
    ]
    df = df.loc[:, df.columns.intersection(selected_cols)]
    df = df.reindex(columns=selected_cols)  # ensure order even if some columns missing
    logger.info("=== Selecting Columns ===")

    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["time_stamp"] = time_stamp
    logger.info("=== Created Timestamp! ===")

    # CSV in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    filename_content = csv_buffer.getvalue()
    logger.info("=== File created in memory! ===")
    logger.info("=== File stored in Filename variable ===")

    today = datetime.now().strftime("%Y-%m-%d")

    # top/bottom 10
    top_negative_10 = df.nsmallest(10, "price_change_percentage_24h")
    top_positive_10 = df.nlargest(10, "price_change_percentage_24h")

    top_negative_10_html = top_negative_10.to_html(index=False, justify="center", border=0)
    top_positive_10_html = top_positive_10.to_html(index=False, justify="center", border=0)

    return {
        "df": df,
        "filename_content": filename_content,
        "today": today,
        "top_negative_10_html": top_negative_10_html,
        "top_positive_10_html": top_positive_10_html,
    }


if __name__ == "__main__":
    # quick local test
    out = fetch_coingecko()
    logger.info(f"=== Rows fetched: {len(out['df'])} ===")
