# DomainHunter: High-Performance Subdomain Scanner

**DomainHunter** is a powerful tool designed to help security researchers and penetration testers efficiently scan and resolve subdomains for a given domain. It supports high concurrency for faster results and can be configured with custom wordlists. The results can be displayed in the console or saved to a file.

## Features

- **High Concurrency**: Perform multiple DNS resolution tasks simultaneously.
- **Custom Wordlist**: Load any wordlist to generate subdomain names.
- **Cross-Platform**: Compatible with Linux, macOS, and Windows.
- **Result Saving**: Optionally save scan results to a file.
- **Progress Bar**: Visual progress indication while scanning.

## Installation

### Requirements

- Python 3.7+
- Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

### Run the Scanner

1. Clone the repository:

```bash
git clone https://github.com/AbuH5/DomainHunter.git
cd DomainHunter
```

2. Run the scanner:

```bash
python main.py -d <domain> -w <wordlist_path> -c <concurrency> -o <output_file>
```

- `-d` : Target domain (e.g., example.com)
- `-w` : Path to the wordlist file (e.g., wordlist.txt)
- `-c` : Number of concurrent tasks (default: 50)
- `-o` : Output file to save results (optional)

## Usage Example

```bash
python main.py -d example.com -w dns-wordlist.txt -c 100 -o results.txt
```
