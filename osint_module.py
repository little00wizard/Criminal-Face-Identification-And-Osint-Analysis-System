# osint_module.py

from googlesearch import search

def run_osint_analysis(name, dob=None, nationality=None):
    """
    Run an OSINT analysis for a person using their name and optional details.
    Returns a report dict and also saves it to a file.
    """
    print(f"[OSINT] Running analysis for: {name}")

    # Simulated data leaks (mock DB)
    fake_osint_data = {
        "osama bin laden": "Found in 3 open data leaks",
        "john doe": "No OSINT records",
        "unknown": "Not available in OSINT DB"
    }

    # Step 1: Check in fake DB
    basic_result = fake_osint_data.get(name.lower(), "No OSINT data found.")

    # Step 2: Simulate online search using Google
    search_results = []
    if name and nationality:
        try:
            query = f"{name} criminal record {nationality}"
            print(f"[OSINT] Searching Google for: {query}")
            search_results = list(search(query, num_results=5))
        except Exception as e:
            search_results = ["[Error] Google search failed.", str(e)]

    # Step 3: Format the result
    report = {
        "name": name,
        "dob": dob,
        "nationality": nationality,
        "data_leak_status": basic_result,
        "search_results": search_results
    }

    # Step 4: Save report to file
    with open("osint_result.txt", "w", encoding="utf-8") as f:
        f.write(f"OSINT Analysis Report for {name}\n")
        f.write(f"DOB: {dob}\nNationality: {nationality}\n\n")
        f.write("== Leak Status ==\n")
        f.write(f"{basic_result}\n\n")
        f.write("== Google Search Results ==\n")
        for link in search_results:
            f.write(link + "\n")

    print("[OSINT] Done. Report saved in osint_result.txt")
    return report
