import ssl
import socket
import sys
import re


#Parse the URL
def parse_url(url, base_hostname=None):
    if not url.startswith("http"):
        if base_hostname:
            url = f"https://{base_hostname}{url}"  #Handle relative URLs
        else:
            url = "https://" + url  #Default to HTTPS if no protocol is specified
    
    protocol, rest = url.split("://", 1)
    parts = rest.split("/", 1)
    hostname = parts[0]
    path = "/" + parts[1] if len(parts) > 1 else "/"  #Path or default to root
    return protocol, hostname, path


def check_http2_support(hostname):
    port = 443
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2', 'http/1.1'])

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            negotiated_protocol = ssock.selected_alpn_protocol()
            return negotiated_protocol == 'h2'  #Return true if HTTP/2 is supported
        
        
#Sending the HTTP request using the ssl library, with redirect handling
def send_request(protocol, hostname, path, max_redirects=5):
    port = 443 if protocol == "https" else 80
    context = ssl.create_default_context() if protocol == "https" else None

    #Create the socket connection
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname) if protocol == "https" else socket.socket(socket.AF_INET)
    conn.connect((hostname, port))

    #Sending HTTP GET request
    request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
    conn.send(request.encode())

    #Get the server response
    response = b""
    while True:
        received = conn.recv(10000)
        if not received:
            break
        response += received
    conn.close()

    #Decode response, using the utf-8 convention since most web uses it. We are ignoring any bytes that cannot be decoded properly
    response = response.decode('utf-8', 'ignore')

    #Check if it's a redirect (301, 302)
    if "HTTP/1.1 301" in response or "HTTP/1.1 302" in response:
        location = re.search(r"Location: (.+?)\r\n", response)
        if location:
            redirect_url = location.group(1).strip()

            #Handle parsed URL components and the full URL
            protocol, new_hostname, new_path = parse_url(redirect_url, base_hostname=hostname)
            
            print(f"Redirected to: {redirect_url}")
            if max_redirects > 0:
                #Following the redirect recursively
                return send_request(protocol, new_hostname, new_path, max_redirects - 1)
            else:
                print("Too many redirects")
                sys.exit(1)


    return response


#Print the response header
def print_response_header(response):
    headers = response.split("\r\n\r\n", 1)[0]
    print("---Response header ---")
    print(headers)
    print("---End of response header---\n")


#Check if there is any cookies in the website and return it's details
def check_cookies(response, hostname):
    cookie_pattern = re.compile(r"Set-Cookie: ([^;]+);.*(domain=[^;]+)?(; expires=[^;]+)?")
    cookies = cookie_pattern.findall(response)

    #Print cookies
    print("2. List of Cookies:")
    for cookie in cookies:  #Looping each cookies
        name = cookie[0].split("=")[0]
        domain = cookie[1].split("=")[1] if cookie[1] else hostname  #Default to hostname if domain deosn't exists
        expires = cookie[2].split("=")[1] if cookie[2] else "Not specified"
        print(f"cookie name: {name}; expires time: {expires}; domain name: {domain}")


#Check if the website is password protected
def check_password_protection(response):
    return "HTTP/1.1 401" in response


def main():
    if len(sys.argv) != 2:
        print("Usage: python web_tester.py <URL>")
        sys.exit(1)

    url = sys.argv[1].strip()
    protocol, hostname, path = parse_url(url)

    
    print(f"website: {hostname}")

    supports_http2 = check_http2_support(hostname)

    response = send_request(protocol, hostname, path)
    
    
    print_response_header(response)
    
    print(f"1. Supports http2: {'yes' if supports_http2 else 'no'}\n")

    check_cookies(response, hostname)

    password_protected = check_password_protection(response)
    print(f"\n3. Password-protected: {'yes' if password_protected else 'no'}")

if __name__ == "__main__":
    main()
