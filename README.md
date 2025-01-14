# WebTester

## Overview
WebTester is a Python-based command-line tool designed to test and analyze web server configurations. It provides insights into HTTP/2 support, cookie management, and password-protected resources, while handling HTTP redirects.

## Features
- **HTTP/2 Support Detection**: Evaluates whether a web server supports HTTP/2 protocol.
- **Redirect Handling**: Recursively follows HTTP redirects (e.g., 301, 302) up to a configurable limit.
- **Cookie Analysis**: Extracts and displays cookie details, including name, domain, and expiration time.
- **Password Protection Check**: Identifies if the website requires authentication (HTTP 401 response).

## Usage
1. Download the file to your own directory.
2. Open a terminal.
3. Navigate to the directory containing `WebTester.py`.
4. Run the program with the following command:
   ```bash
   python WebTester.py <URL>
   ```
   Replace `<URL>` with the URL of the website you want to test. For example:
   ```bash
   python WebTester.py https://example.com
   ```

## Example Output
```text
website: example.com
1. Supports http2: yes

---Response header ---
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
...
---End of response header---

2. List of Cookies:
cookie name: sessionid; expires time: Not specified; domain name: example.com

3. Password-protected: no
```
