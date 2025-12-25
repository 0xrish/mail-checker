# 📧 Advanced Email Checker & Verifier (Rust-Powered)

Verify the existence of any email address in real-time without ever sending a single message. This high-performance Apify Actor uses a specialized Rust engine to perform deep SMTP handshakes, MX record validation, and provider-specific checks (Gmail, Yahoo, Outlook) with extreme speed and accuracy.

## 🚀 Key Features

- **No Emails Sent**: Validates addresses using SMTP handshakes—completely invisible to the recipient.
- **High Performance**: Built on a multi-threaded Rust core with parallel processing for massive batch lists.
- **Smart Provider Support**: Specialized logic for Gmail, Yahoo, and Outlook, including headless browser verification for difficult providers.
- **Deep Validation**: Checks syntax, MX records, SMTP deliverability, and catch-all status.
- **Security & Privacy**: Support for SOCKS5 proxies to ensure high deliverability and avoid IP blocking.
- **Enrichment**: Optional Gravatar image detection and HaveIBeenPwned breach checks.

## 🛠️ How to Use

1. **Input Emails**: Provide a single email or a list of emails in the input JSON.
2. **Configure (Optional)**: Set your `from_email` and `hello_name` (recommended to use your own domain for better results).
3. **Run**: Start the Actor. It will process your list in parallel.
4. **Get Results**: Download your verified list in JSON, CSV, or Excel format from the Apify Dataset.

## 📥 Input Parameters

| Field | Type | Description |
|-------|------|-------------|
| `email` | String | A single email address to verify. |
| `emails` | Array | A list of email addresses for batch verification. |
| `smtp_timeout` | Integer | Timeout per connection (default: 15s). Lower for speed, higher for accuracy. |
| `proxy_url` | String | SOCKS5 proxy URL (e.g., `socks5://user:pass@host:port`). |
| `check_gravatar` | Boolean | Check if the email has an associated Gravatar profile. |
| `haveibeenpwned_api_key` | String | (Optional) Check if the email has appeared in known data breaches. |

## 📤 Output Data

The Actor provides a detailed JSON object for every email checked:

```json
{
  "input": "test@gmail.com",
  "is_reachable": "safe",
  "syntax": {
    "is_valid": true,
    "normalized": "test@gmail.com"
  },
  "mx": {
    "accepts_mail": true,
    "records": ["gmail-smtp-in.l.google.com."]
  },
  "smtp": {
    "can_connect_smtp": true,
    "is_deliverable": true,
    "is_catch_all": false
  },
  "misc": {
    "is_disposable": false,
    "is_role_account": false,
    "gravatar_url": "https://..."
  }
}
```

## 💡 Use Cases

- **Lead Generation**: Clean your cold email lists to maintain a high sender reputation.
- **User Signups**: Validate user emails in real-time during registration to prevent fake accounts.
- **Database Cleaning**: Periodically scrub your CRM to remove dead or invalid addresses.
- **Security**: Identify disposable or high-risk email addresses.

## 🔒 Privacy & Compliance

This Actor does not store any of the emails you process. All checks are performed in real-time and results are stored only in your private Apify Dataset.

---
