# 🟢 BestChange Parser

An asynchronous Python-based parser for extracting real-time exchange rate data from the [BestChange](https://www.bestchange.com/) API and saving it to a database.

This project supports automatic currency pair generation, scheduled updates, and safe insertion of rates into a local database (SQLite, but can be adapted to MySQL/PostgreSQL).

---

## 🚀 Features

- Fully **async** implementation with `aiohttp`  
- Automatically generates all valid exchange currency pairs  
- Integrates with **BestChange API** (v2)  
- Retrieves and updates `bestchange_id` for new coins if missing  
- Stores data in `exchange_exchangerate` table with rate, min/max amounts, and timestamp  
- Handles large volumes of data with chunked requests  
- Logs updates, skips, and errors for reliability  
- Designed to run in a **looped environment** for continuous background parsing

---

## 🧱 Tech Stack

- Python 3.10+  
- aiohttp  
- SQLite (via `aiosqlite`, easily adaptable to MySQL/PostgreSQL)  
- Custom database access layer using `aiosqlite`

---

## 📦 Project Structure

```
.
├── main.py                    # Main loop for data parsing
├── config.py                  # API key and config variables
└── database/
    ├── connect.py             # Async DB connection
    └── crud.py                # Insert, update, fetch logic
```

---

## 🔧 How It Works

1. Fetches all slugs from the `exchange_coin` table and resolves their `bestchange_id` if missing
2. Generates all valid coin-to-coin combinations (excluding identical ones)
3. Sends chunked requests to the BestChange API (up to 500 pairs per call)
4. Extracts the best rate for each pair, along with minimum and maximum available exchange amounts
5. Saves all data into the `exchange_exchangerate` table with a timestamp
6. Runs in a continuous loop with retry handling (every 10 seconds by default)

---

## 🗂 Example Use Cases

This parser can be used as a foundation for:

- Cryptocurrency exchange rate aggregators  
- Arbitrage monitoring bots  
- Telegram or Discord bots  
- Financial analytics dashboards  
- Alerts and notification systems

---

## ⚙ Configuration

Add your `API_KEY` to `config.py`:

```python
API_KEY = "your_bestchange_api_key"
```

---

## 📬 Contributing

Feel free to fork the repo, submit issues, or suggest improvements.

---

**Author:** artyomkap  
**License:** MIT

