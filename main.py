import asyncio
import aiodns
import argparse
import socket
import logging
import sys
import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
import pyfiglet
import os

console = Console()

class DNSResolver:
    def __init__(self):
        self.resolver = aiodns.DNSResolver()

    async def resolve(self, subdomain: str) -> list[str]:
        try:
            result = await self.resolver.gethostbyname(subdomain, socket.AF_UNSPEC)
            return result.addresses
        except aiodns.error.DNSError:
            return []
        except Exception as e:
            logging.error(f"Error resolving {subdomain}: {e}")
            return []


class SubdomainScanner:
    def __init__(self, domain: str, wordlist: list[str], concurrency: int, output_file: str = None):
        self.domain = domain
        self.wordlist = wordlist
        self.concurrency = concurrency
        self.output_file = output_file
        self.results = []
        self.dns_resolver = DNSResolver()

    def generate_subdomains(self) -> list[str]:
        return [f"{word}.{self.domain}" for word in self.wordlist if word]

    async def resolve_subdomain(self, subdomain: str, progress, task_id):
        start_time = time.time()
        resolved_ips = await self.dns_resolver.resolve(subdomain)
        duration = time.time() - start_time
        if resolved_ips:
            result = f"[green]{subdomain}[/green] -> [cyan]{', '.join(resolved_ips)}[/cyan] ([yellow]{duration:.2f}s[/yellow])"
            console.print(result)
            self.results.append(f"{subdomain} -> {', '.join(resolved_ips)} {duration:.2f}")
        progress.update(task_id, advance=1)

    async def scan(self):
        subdomains = self.generate_subdomains()
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task_id = progress.add_task("[cyan]Scanning Subdomains...", total=len(subdomains))
            for i in range(0, len(subdomains), self.concurrency):
                batch = subdomains[i:i + self.concurrency]
                tasks = [self.resolve_subdomain(subdomain, progress, task_id) for subdomain in batch]
                await asyncio.gather(*tasks)
        if self.output_file:
            self.save_results()

    def save_results(self):
        try:
            with open(self.output_file, "w", encoding="utf-8") as file:
                file.writelines(f"{result}\n" for result in self.results)
            console.print(f"[bold green]Results saved to:[/bold green] {self.output_file}")
        except IOError as e:
            logging.error(f"Error saving results: {e}")


class WordlistLoader:
    @staticmethod
    def load(file_path: str) -> list[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logging.error(f"Wordlist file '{file_path}' not found.")
            return []
        except IOError as e:
            logging.error(f"Error reading wordlist file: {e}")
            return []


class ScannerApp:
    @staticmethod
    async def run(domain: str, wordlist_path: str, concurrency: int, output_file: str):
        wordlist = WordlistLoader.load(wordlist_path)
        if not wordlist:
            console.print("[red]No words found in the wordlist. Exiting.[/red]")
            return
        scanner = SubdomainScanner(domain, wordlist, concurrency, output_file)
        try:
            console.print(f"[bold green]Starting scan for domain:[/bold green] {domain}")
            await scanner.scan()
        except KeyboardInterrupt:
            console.print("\n[bold red]Scan interrupted by user.[/bold red]")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


def setup_logging():
    logging.basicConfig(
        filename="scanner_errors.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description="High-Performance Subdomain Scanner")
    parser.add_argument("-d", "--domain", required=True, help="The target domain name")
    parser.add_argument("-w", "--wordlist", required=True, help="The wordlist file")
    parser.add_argument("-c", "--concurrency", type=int, default=50, help="Number of concurrent tasks (default: 50)")
    parser.add_argument("-o", "--output", help="File to save the results")
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()
    args = parse_arguments()

    ascii_logo = pyfiglet.figlet_format("DomainHunter", font="slant")
    console.print(f"[bold magenta]{ascii_logo}[/bold magenta]")

    # Set event loop policy for Windows platform
    if sys.platform.startswith("win"):
        if asyncio.get_event_loop_policy().__class__.__name__ == "WindowsProactorEventLoopPolicy":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Ensure compatibility across all platforms
    asyncio.run(ScannerApp.run(args.domain, args.wordlist, args.concurrency, args.output))
