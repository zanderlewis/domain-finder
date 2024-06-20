import random
import whois
import nltk
import argparse
from nltk.corpus import words
import socket
import logging

logging.getLogger('whois').setLevel(logging.CRITICAL)

# nltk.download('words')

shouldPrint = True


def p(text):
    """Print text if the verbose flag is set."""
    if shouldPrint:
        print(text)


def generate_random_words(word_list, count=10):
    """Generate a list of random words from the provided word list."""
    return random.sample(word_list, count)


def is_domain_available(domain):
    """Check if the domain is available."""
    try:
        # First, try a whois lookup
        domain_info = whois.whois(domain)
        if domain_info.status is None:
            # If the whois lookup shows the domain is available, confirm with a DNS lookup
            try:
                socket.gethostbyname(domain)
                return False  # If the DNS query did not fail, the domain is taken
            except socket.gaierror:
                return True  # If the DNS query failed, the domain is available
        else:
            return False  # If the whois lookup shows the domain is taken
    except (whois.parser.PywhoisError, Exception):
        # If the whois lookup fails, assume the domain is taken
        return False


def find_available_domains(word_list, custom_words, tlds, count=10):
    """Find a specified number of available domains with a specified TLD from a word list."""
    available_domains = []
    taken_domains = []
    checked_domains = set()
    attempts = 1

    # Prioritize custom words
    if custom_words:
        p("===================\nChecking custom words first...\n===================")
        for word in custom_words:
            tld = random.choice(tlds)  # Select a random TLD
            domain = word.strip().lower() + "." + tld
            if domain not in checked_domains:
                checked_domains.add(domain)
                if is_domain_available(domain):
                    available_domains.append(domain)
                    p(f"Available: {domain}")
                else:
                    p(f"Taken: {domain}")
                if len(available_domains) >= count:
                    return available_domains
        p(
            "===================\nFinished checking custom words. Starting dictionary words...\n==================="
        )
    else:
        p("===================\nStarting dictionary words...\n===================")

    # If not enough domains found, continue with random words
    word_list_copy = word_list.copy()  # Create a copy of word_list
    while len(available_domains) < count and word_list_copy:
        word = random.sample(list(word_list_copy), 1)[0].strip().lower()
        tld = random.choice(tlds)  # Select a random TLD
        domain = word + "." + tld
        if domain not in checked_domains:
            checked_domains.add(domain)
            if is_domain_available(domain):
                available_domains.append(domain)
                p(f"Available: {domain}")
            else:
                taken_domains.append(domain)
                p(f"Taken: {domain}")
        if word in word_list_copy:  # Check if word exists in the list before removing
            word_list_copy.remove(word)  # Remove word from the copy of word_list

        attempts += 1

    p("===================\nFinished.\n===================")
    print(f"Attempted {attempts} domains...")
    print(f"Found {len(available_domains)} available domains.")
    print(f"{len(taken_domains)} checked domains are taken.")

    return available_domains


def filter_words(word_list, startswith=None, endswith=None):
    """Filter the word list based on the startswith and endswith parameters."""
    if startswith:
        word_list = [word for word in word_list if word.startswith(startswith)]
    if endswith:
        word_list = [word for word in word_list if word.endswith(endswith)]
    return word_list


def get_shortest_domains(domains, count=15):
    """Get the specified number of shortest domains."""
    # Sort the domains by length and return the shortest ones
    return sorted(domains, key=len)[:count]


def run():
    parser = argparse.ArgumentParser(description="Find available domains.")
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=10,
        help="The number of available domains to find.",
    )
    parser.add_argument(
        "--tld", "-t", nargs="*", default=["com"], help="The TLDs for the domains."
    )
    parser.add_argument(
        "--startswith", "-s", help="Filter words that start with this string."
    )
    parser.add_argument(
        "--endswith", "-e", help="Filter words that end with this string."
    )
    parser.add_argument("--customwords", nargs="*", help="Custom words to look for.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output.")
    parser.add_argument(
        "--shortest", action="store_true", help="Show the shortest 15 domains."
    )
    args = parser.parse_args()

    global shouldPrint
    shouldPrint = args.verbose

    # Get the list of English words from the NLTK corpus
    word_list = words.words()
    if args.customwords:
        word_list += args.customwords
    word_list = filter_words(word_list, args.startswith, args.endswith)

    custom_words = args.customwords if args.customwords else []
    available_domains = find_available_domains(
        word_list, custom_words, args.tld, args.count
    )

    if args.shortest:
        short = get_shortest_domains(available_domains)

    print(f"\nAvailable domains:")
    for domain in available_domains:
        print(domain)

    if args.shortest:
        print("\nShortest domains:")
        for domain in short:
            print(domain)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
