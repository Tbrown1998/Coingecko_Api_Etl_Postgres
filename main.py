import schedule
import time
from etl.utils import get_logger
from etl.extract import fetch_coingecko
from etl.load import create_database_if_not_exists, get_sqlalchemy_engine, create_table_if_not_exists, upsert_daily_data
from etl.emailer import send_mail
from configs import settings

logger = get_logger(__name__)


def run_etl():
    logger.info("=== ETL run started ===")
    try:
        # Extract
        out = fetch_coingecko()
        df = out["df"]
        filename_content = out["filename_content"]
        today = out["today"]
        top_negative_10_html = out["top_negative_10_html"]
        top_positive_10_html = out["top_positive_10_html"]

        # Load
        create_database_if_not_exists()
        engine = get_sqlalchemy_engine()
        create_table_if_not_exists(engine, table_name="crypto_data")
        upsert_daily_data(engine, df, table_name="crypto_data")

        # Email
        subject = f"ETL Project (Top 10 crypto currency data to invest for {today})"

        # Keep the original HTML body exactly (we reuse the same style + content)
        style = """
            <style>
            body {
                font-family: Arial, sans-serif;
                color: #222;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }
            h2 {
                color: #1a73e8;
                margin-bottom: 8px;
            }
            p {
                font-size: 15px;
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
                margin-bottom: 30px;
                font-size: 14px;
            }
            th, td {
                border: 1px solid #ddd;
                text-align: center;
                padding: 8px;
            }
            th {
                background-color: #eaf1fb;
                color: #222;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .footer {
                font-size: 13px;
                color: #666;
                margin-top: 30px;
            }
            </style>
            """

        body = f"""
            <html>
            <head>{style}</head>
            <body>
                <h2>Good Morning! ☀️</h2>
                <p>Your CoinGecko crypto report is here!</p>

                <p>
                The CoinGecko crypto data for <strong>{today}</strong> has been successfully pulled from the CoinGecko API
                and appended to your <strong>PostgreSQL database</strong> for analysis.
                Attached is a full CSV snapshot for your crypto records, and below is a quick summary of today’s market movements.
                </p>

                <h2>📈 Top 10 Cryptos with Highest Price Increase (24h)</h2>
                {top_positive_10_html}

                <h2>📉 Top 10 Cryptos with Highest Price Decrease (24h)</h2>
                {top_negative_10_html}

                <div class="footer">
                <p>Best regards,</p>
                <p><strong>Oluwatosin Amosu,</strong><br> 
                    Senior Data Analyst,<br>
                    Baby Data Engineer
                </p>
                
                <br> <!-- spacing -->
                
                <p>
                    <em>Tbrown's Automated Python ETL Project</em><br>
                    This is an automated email, please do not reply!.<br>
                    See you tomorrow!
                </p>
                </div> 
                </body> 
                </html> """

        send_mail(subject, body, filename_content, today)
        logger.info("=== ETL run finished successfully ===")

    except Exception as err:
        logger.error(f"=== ETL run failed: {err} ===")


def schedule_job():
    run_time = settings.SCHEDULE_TIME
    schedule.every().day.at(run_time).do(run_etl)
    logger.info(f"=== Scheduled job set to run daily at {run_time} ===")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # If you want to run once immediately, uncomment:
     run_etl()

    # # Run scheduled
    # schedule_job()
