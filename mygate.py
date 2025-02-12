import requests
import uuid
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

BASE_URL = "https://api.mygate.network"

def load_proxies():
    try:
        with open("proxy.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        console.print("[bold red]File proxy.txt not found. Using no proxy.[/bold red]")
        return []

def load_token():
    try:
        with open("token.txt", "r") as file:
            token = file.read().strip()
        return token
    except FileNotFoundError:
        console.print("[bold red]File token.txt not found. Exiting...[/bold red]")
        exit(1)

def generate_headers(token):
    return {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "access-control-allow-origin": "*",
        "authorization": f"Bearer {token}",
        "if-none-match": 'W/"85a-H6W3+d4pFjJqkgEmWD+T1nfoi44"',
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "x-requested-store": "default",
        "x-requested-with": "XMLHttpRequest",
    }

def get_request(path, headers, proxy=None):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            console.print(f"[bold green]GET Request Successful with Proxy: {proxy['http'] if proxy else 'No Proxy'}[/bold green]")
        return response
    except requests.RequestException as e:
        console.print(f"[bold red]GET Request Failed with Proxy: {proxy['http'] if proxy else 'No Proxy'} - {e}[/bold red]")
        return None

def post_request(path, data, headers, proxy=None):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.post(url, json=data, headers=headers, proxies=proxy, timeout=10)
        if response.status_code in [200, 201]:
            console.print(f"[bold green]POST Request Successful with Proxy: {proxy['http'] if proxy else 'No Proxy'}[/bold green]")
        return response
    except requests.RequestException as e:
        console.print(f"[bold red]POST Request Failed with Proxy: {proxy['http'] if proxy else 'No Proxy'} - {e}[/bold red]")
        return None

def generate_node_id():
    return str(uuid.uuid4())

def check_node_quality(headers, proxy=None):
    path = "/api/front/metadata/nodes/quality"
    response = get_request(path, headers, proxy)
    if response and response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Failed to check node quality. Status Code: {response.status_code if response else 'N/A'}[/bold red]")
        return None

def main():
    # Create a colorful and styled "KONTLIJO" text
    kontlijo_text = Text(justify="center")
    kontlijo_text.append("K", style="bold red")
    kontlijo_text.append("O", style="bold green")
    kontlijo_text.append("N", style="bold yellow")
    kontlijo_text.append("T", style="bold blue")
    kontlijo_text.append("L", style="bold magenta")
    kontlijo_text.append("I", style="bold cyan")
    kontlijo_text.append("J", style="bold white")
    kontlijo_text.append("O", style="bold green")

    # Display the banner with the styled "KONTLIJO" text centered
    console.print(Panel(kontlijo_text, title="Welcome", subtitle="Stay Connected", style="bold cyan", expand=False))

    proxies = load_proxies()
    token = load_token()
    headers = generate_headers(token)
    proxy_index = 0

    while True:
        proxy = None
        if proxies:
            proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}
            proxy_index = (proxy_index + 1) % len(proxies)

        node_id = generate_node_id()
        console.print(f"[bold green]Generated Node ID:[/bold green] [cyan]{node_id}[/cyan]")

        post_data = {
            "id": node_id,
            "status": "Good",
            "metadata": {
                "type": "example",
                "description": "Auto-generated node"
            }
        }
        response = post_request("/api/front/nodes", post_data, headers, proxy)
        if response and (response.status_code == 201 or response.status_code == 200):
            console.print("[bold green]Node created successfully![/bold green]")
            console.print(f"[bold]Response:[/bold] {response.json()}")
        else:
            console.print(f"[bold red]Failed to create node. Status Code: {response.status_code if response else 'N/A'}[/bold red]")
            console.print(f"[bold]Response:[/bold] {response.text if response else 'No response'}")

        console.print("\n[bold yellow]Checking node quality...[/bold yellow]")
        quality_response = check_node_quality(headers, proxy)
        if quality_response:
            table = Table(title="Node Quality Report")
            table.add_column("Metric", style="bold cyan")
            table.add_column("Value", style="bold magenta")

            for key, value in quality_response.items():
                table.add_row(key.capitalize(), str(value))

            console.print(table)

        console.print("[bold blue]Waiting for 5 seconds before the next sync...[/bold blue]\n")
        time.sleep(5)

if __name__ == "__main__":
    main()