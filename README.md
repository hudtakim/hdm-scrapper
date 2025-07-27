# App Review Scraper API

This project is a Flask-based web API for scraping reviews from a specific app (e.g., Google Play Store). It provides secure access using token authentication and supports exporting reviews in JSON, CSV, or Excel format.

## Features

- Token-based authentication for API access
- Scrapes reviews based on provided app ID
- Returns results in JSON format by default
- Option to export reviews as CSV or Excel (.xlsx)
- Admin endpoint to update the authentication token

---

## Requirements

- Python 3.8+
- Flask
- Pandas

Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```txt
flask
pandas
```

---

## API Endpoints

### 1. **Update Token**

**POST** `/api/update_token`

Used to set or update the API access token.

#### Request Body (JSON):

```json
{
  "new_token": "your_new_token_here",
  "admin_key": "optional_admin_key"
}
```

#### Response:

```json
{
  "message": "Token updated successfully",
  "new_token": "your_new_token_here"
}
```

---

### 2. **Scrape Reviews**

**GET** `/api/reviews`

Used to fetch app reviews using the provided `app_id`.

#### Query Parameters:

| Parameter    | Type    | Description                                         |
| ------------ | ------- | --------------------------------------------------- |
| requestToken | string  | Required. The token used for authentication.        |
| app\_id      | string  | Required. The app ID to scrape reviews from.        |
| count        | integer | Optional. Number of reviews to fetch (default: 10)  |
| save\_csv    | boolean | Optional. If `true`, returns reviews as CSV file.   |
| save\_excel  | boolean | Optional. If `true`, returns reviews as Excel file. |

#### Example Request:

```
GET /api/reviews?requestToken=abc123&app_id=com.example.app&count=5&save_csv=true
```

#### Example JSON Response:

```json
[
  {
    "author": "John Doe",
    "rating": 5,
    "review": "Great app!"
  },
  {
    "author": "Jane Smith",
    "rating": 4,
    "review": "Works fine, could use improvements."
  }
]
```

---

## Output Format

- JSON (default)
- CSV (if `save_csv=true`)
- Excel (if `save_excel=true`)

> Files are served as attachments when exporting in CSV or Excel format.

---

## File Structure

```
project/
├── app.py
├── scraper.py
├── token_store.json
├── README.md
├── requirements.txt
└── (generated review CSV/XLSX files)
```

---

## Notes

- Only one valid token is stored at a time in `token_store.json`.
- Temporary review export files are not automatically deleted; clean them up periodically if needed.

---

## License

MIT License

