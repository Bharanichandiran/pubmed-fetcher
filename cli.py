import argparse
import csv
from pubmed_fetcher.fetcher import fetch_pubmed_ids, fetch_paper_details

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with company-affiliated authors.")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("-f", "--file", help="Output CSV filename")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    pmids = fetch_pubmed_ids(args.query)
    papers = [fetch_paper_details(pmid) for pmid in pmids]
    papers = [p for p in papers if p]

    if not papers:
        print("No company-affiliated papers found.")
        return

    if args.file:
        with open(args.file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=papers[0].keys())
            writer.writeheader()
            writer.writerows(papers)
    else:
        for paper in papers:
            print(paper)

if __name__ == "__main__":
    main()
