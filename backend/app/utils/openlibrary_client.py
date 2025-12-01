# app/utils/openlibrary_client.py

import requests

def fetch_json(url: str) -> dict:
    """Safe wrapper for requests.get()."""
    try:
        return requests.get(url, timeout=10).json(), True
    except Exception:
        return {}, False

def follow_work_redirect(work_key: str) -> dict:
    """
    Fetch a Work entry and follow redirect if needed.
    """
    url = f"https://openlibrary.org{work_key}.json"
    data, ok = fetch_json(url)
    
    if not ok:
        return {}, False

    # If redirect, follow the new location
    if data.get("type", {}).get("key") == "/type/redirect":
        new_location = data.get("location")
        if new_location:
            return follow_work_redirect(new_location)

    return data, True

def fetch_subjects_from_openlibrary(isbn: str) -> list[str]:
    """
    Fetches subjects from BOTH:
    - Edition record (/isbn/)
    - Work record (/works/)
    Merges them, removes duplicates, prints everything for debugging.
    """

    print(f"\n🔎 Fetching subjects for ISBN {isbn} ...")

    # -------- GET EDITION DATA --------
    edition_url = f"https://openlibrary.org/isbn/{isbn}.json"
    edition_data, ok1 = fetch_json(edition_url)

    if not ok1:
        print("  ❌ Network error on edition call.")
        return [], False
    
    if not edition_data:
        print("  ❌ No edition data found.")
        return []

    subjects = []

    # Edition-level subjects
    edition_subjects = edition_data.get("subjects", [])
    print(f"  📘 Edition subjects: {edition_subjects if edition_subjects else 'NONE'}")
    if isinstance(edition_subjects, list):
        subjects.extend(edition_subjects)

    # -------- GET WORK DATA --------
    works = edition_data.get("works", [])
    if not works:
        print("  ❌ No works listed for this ISBN.")
        merged = list(set(subjects))
        print(f"  ✅ Merged subjects: {merged}")
        return merged, True
    
    
    work_key = works[0].get("key")
    if not work_key:
        print("  ❌ Invalid work key.")
        merged = list(set(subjects))
        print(f"  ✅ Merged subjects: {merged}")
        return merged, True
    
    # Follow redirects
    work_data, ok2 = follow_work_redirect(work_key)
    
    if not ok2:
        print("  ❌ Network error on work call.")
        return [], False

    # Work-level subjects
    work_subjects = work_data.get("subjects", [])
    print(f"  📕 Work subjects: {work_subjects if work_subjects else 'NONE'}")
    if isinstance(work_subjects, list):
        subjects.extend(work_subjects)


    # -------- MERGE + CLEAN --------
    merged = list(set([s for s in subjects if isinstance(s, str)]))
    print(f"  ✅ Merged subjects: {merged}")

    return merged, True
