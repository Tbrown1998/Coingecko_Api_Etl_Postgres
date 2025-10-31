
# 🧠 ETL Project: CoinGecko Cryptocurrency Data Pipeline

### 📋 Overview
This ETL (Extract, Transform, Load) Python script automates the process of fetching cryptocurrency data from the **CoinGecko API**, cleaning and transforming it with **pandas**, storing it in a **PostgreSQL** database, and sending an automated email report (with a CSV attachment and summary tables).

The pipeline is scheduled to run daily using the **schedule** library.

---

## 🚀 Features
- **Data Extraction:** Fetches live market data (top 250 cryptos) from the CoinGecko API.
- **Data Transformation:** Cleans and structures the data using pandas.
- **Data Loading:** Stores data into a PostgreSQL database, replacing daily entries dynamically.
- **Email Automation:** Sends daily crypto market summary reports via email (in-memory CSV attachment).
- **Scheduling:** Runs automatically every morning at 09:00.

---

## ⚙️ Tech Stack & Libraries
| Category | Libraries |
|-----------|------------|
| Data Extraction | `requests` |
| Data Transformation | `pandas`, `datetime` |
| Database Connection | `psycopg2`, `SQLAlchemy` |
| Email Automation | `smtplib`, `email.mime`, `io` |
| Scheduling | `schedule`, `time` |

---

## 🧩 Script Structure

### 1️⃣ Function: `send_mail()`
Handles email composition and delivery with the following key features:
- Sends emails through Gmail’s SMTP server.
- Supports multiple recipients.
- Attaches CSV file from memory (no local file storage).
- Accepts `subject`, `body`, `filename`, and `today` parameters.

**Attachment Naming:**
Each attachment includes a timestamp, e.g.:
```
crypto_data_2025-10-29.csv
```

**Usage:**
```python
send_mail(subject, body, filename, today)
```

---

### 2️⃣ Function: `get_crypto_data()`
Fetches crypto data from CoinGecko and processes it for database storage and reporting.

**Workflow Steps:**
1. **Extract** — Calls CoinGecko API to fetch top 250 cryptos by market cap.
2. **Transform** — Selects key columns (`id`, `symbol`, `name`, `price`, etc.), adds timestamp.
3. **Load** — Checks PostgreSQL for existing data for the day; deletes and replaces it with fresh data.
4. **Email** — Generates HTML summary and sends an automated report email with top 10 gainers and losers.

---

### 3️⃣ Database Logic
- Connects to PostgreSQL using psycopg2.
- Creates `crypto_db` database if not found.
- Creates table `crypto_data` dynamically if not existing.
- Deletes and replaces only today’s data (keeps historical data intact).

**Schema Example:**
```sql
CREATE TABLE crypto_data (
    id VARCHAR(100),
    symbol VARCHAR(50),
    name VARCHAR(150),
    current_price DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    price_change_percentage_24h DOUBLE PRECISION,
    ath DOUBLE PRECISION,
    atl DOUBLE PRECISION,
    time_stamp TIMESTAMP
);
```

---

### 4️⃣ Email Summary (HTML Body)
The email body is built using HTML for better readability, containing:
- A greeting header.
- Data summary description.
- Two formatted tables:
  - Top 10 coins with highest price increase.
  - Top 10 coins with largest price decrease.
- A professional footer with author info.

**Footer Example:**
```html
<div class="footer">
  <p>Best regards,</p>
  <p><strong>Oluwatosin Amosu</strong><br>
     Senior Data Analyst<br>
     Baby Data Engineer
  </p>
  <br>
  <p>
    <em>Tbrown's Automated Python ETL Project</em><br>
    This is an automated email — please do not reply.<br>
    See you tomorrow!
  </p>
</div>
```

---

### 5️⃣ Scheduling
The task runs automatically each day at **9:00 AM** using `schedule`:

```python
schedule.every().day.at('09:00').do(get_crypto_data())
```

To run immediately (without scheduling):
```python
get_crypto_data()
```

---

## 🧠 How to Use

### 🔹 1. Setup Environment
Install dependencies:
```bash
pip install pandas requests psycopg2-binary SQLAlchemy schedule
```

### 🔹 2. Update PostgreSQL Credentials
In the script, locate:
```python
conn = psycopg2.connect(
    host="",
    dbname="",
    user="",
    password="",
    port=""
)
```
and insert your database credentials.

### 🔹 3. Update Email Details
In the `send_mail()` function:
- Add your Gmail credentials (`sender_mail`, `email_password`).
- Provide recipients list:
  ```python
  receiver_mails = ["example1@gmail.com", "example2@yahoo.com"]
  ```

### 🔹 4. Run the ETL
```bash
python etl_v1_coingecko_api.py
```

You’ll see progress logs like:
```
=== Connection Successful!, Getting Data!... ===
=== Succefully Connected With Postgres ===
=== mail sent successfully! ===
```

---

## 🧠 Author
**Oluwatosin Amosu (Tbrown)**  
*Senior Data Analyst*  

💼 Automated ETL Project built in Python for daily crypto reporting.

---

### 🕒 Version
**Script:** `etl_v1_coingecko_api.py`  
**Version:** 1.0  
**Date:** October 2025

---

> 🧩 _This project automates the end-to-end cryptocurrency data reporting pipeline, integrating live API data, PostgreSQL storage, and daily email summaries._
