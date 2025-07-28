from typing import List, Dict, Optional
from Bio import Entrez
import logging

Entrez.email = "bharanichandran@gmail.com"

ACADEMIC_KEYWORDS = ["university", "institute", "college", "school"]
COMPANY_KEYWORDS = ["pharma", "biotech", "inc", "ltd", "corp", "gmbh", "sas", "llc"]

def is_non_academic(affiliation: str) -> bool:
    return not any(keyword in affiliation.lower() for keyword in ACADEMIC_KEYWORDS)

def is_company_affiliation(affiliation: str) -> bool:
    return any(keyword in affiliation.lower() for keyword in COMPANY_KEYWORDS)

def fetch_pubmed_ids(query: str, max_results: int = 20) -> List[str]:
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    return record["IdList"]

def fetch_paper_details(pmid: str) -> Optional[Dict]:
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    records = Entrez.read(handle)
    try:
        article = records['PubmedArticle'][0]['MedlineCitation']['Article']
        title = article['ArticleTitle']
        authors = article.get('AuthorList', [])
        pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
        date = f"{pub_date.get('Year', '')}-{pub_date.get('Month', '')}"
        non_academic_authors = []
        companies = []
        email = None

        for author in authors:
            affil = author.get("AffiliationInfo", [{}])[0].get("Affiliation", "")
            if affil and is_non_academic(affil):
                name = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
                non_academic_authors.append(name)
                if is_company_affiliation(affil):
                    companies.append(affil)
                if "@" in affil and not email:
                    email = affil.split()[-1].strip('.,;()')

        if non_academic_authors:
            return {
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": date,
                "Non-academic Author(s)": "; ".join(non_academic_authors),
                "Company Affiliation(s)": "; ".join(companies),
                "Corresponding Author Email": email or ""
            }
    except Exception as e:
        logging.debug(f"Error processing PMID {pmid}: {e}")
    return None
