"""
Phase 2 — Data Collection
Scraper: Meta Transparency Center (Facebook / Instagram)
Community Standards Enforcement Report — official CSV export (v4, FINAL)

WHY THIS VERSION EXISTS
------------------------
v1-v3 tried progressively more complex ways to extract data from the
rendered page (text parsing, then capturing internal GraphQL network
responses). Investigation of the live site found something much better:
every report page has a "Download (CSV)" button, and clicking it exports
the ENTIRE report — every policy category, every quarter back to 2017,
BOTH Facebook and Instagram — as one official, Meta-published CSV file.
This was confirmed by downloading from two different pages (Hateful
Conduct and the Overview page) and comparing: identical 5,410-row files.

This is a far better data source than anything scraped or reverse
engineered: it's an official export, not an inferred/captured value, which
is a much stronger methodological claim for the dissertation than "we
captured the site's internal API traffic."

WHAT THIS SCRIPT DOES
----------------------
1. Configures headless Chrome to auto-download files (no save-dialog) into
   a known folder.
2. Loads the Overview page.
3. Finds and clicks the "Download (CSV)" button (this one has real visible
   text, unlike the icon-only Facebook/Instagram toggle we fought with in
   v3 — so a simple text-based element search is reliable here).
4. Waits for the CSV to actually land on disk, then copies it into
   data/raw/ with a timestamped filename, and loads it with pandas to
   report back basic shape/validation info (row count, columns, apps
   present) so you can immediately see whether the download worked.

UNTESTED CAVEAT: the auto-download Chrome configuration and the button
click are both new code paths not yet verified against the live site by
me — only manually confirmed by you in the browser. If the automated
click doesn't trigger the download the way manual clicking did, that's
useful diagnostic information, not a sign the overall approach is wrong.
"""

import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OVERVIEW_URL = "https://transparency.meta.com/reports/community-standards-enforcement/"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "_downloads_tmp"
PAGE_LOAD_TIMEOUT = 20
DOWNLOAD_WAIT_TIMEOUT = 30  # seconds to wait for the CSV to actually appear on disk


def build_driver() -> webdriver.Chrome:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # IMPORTANT: headless Chrome defaults to a small ~800x600 window. Meta's
    # site is responsive, and at narrow widths this Download button may be
    # hidden inside a collapsed menu or restructured entirely — which would
    # explain why every element search so far has found nothing at all.
    # Forcing a full desktop-sized viewport avoids that mismatch.
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
    # Auto-download to our folder without a save dialog (headless Chrome
    # needs this set via prefs, not just a download.default_directory arg)
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    # Headless Chrome disables downloads by default for security reasons.
    # Two different CDP commands exist for re-enabling them depending on
    # Chrome version/headless mode — Page-level (older) and Browser-level
    # (newer "--headless=new" mode often specifically needs this one).
    # Setting both maximises the chance one of them actually takes effect.
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": str(DOWNLOAD_DIR)},
    )
    try:
        driver.execute_cdp_cmd(
            "Browser.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": str(DOWNLOAD_DIR),
                "eventsEnabled": True,
            },
        )
    except Exception as e:
        print(f"[meta_scraper] Browser.setDownloadBehavior not available: {e}")
    return driver


def wait_for_render(driver, min_chars: int = 200):
    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
        lambda d: len(d.find_element(By.TAG_NAME, "body").text.strip()) > min_chars
    )
    time.sleep(2)


def click_download_csv(driver) -> bool:
    """
    Find and click the 'Download (CSV)' element. DOM inspection confirmed
    it's a leaf <span> (no child elements) with Meta's atomic-CSS utility
    classes. Two earlier attempts failed for different reasons:
      - searching all descendant text (`.`) matched a <script> tag whose
        JS source happened to contain the word "download"
      - searching only direct text() nodes matched nothing, because the
        visible text is likely split across multiple text nodes and
        XPath's text() + normalize-space() only evaluates the first one
    This version restricts to <span> elements with no child elements
    (not(*)) — ruling out <script>/<div> wrappers structurally rather than
    by name — and uses string(.), which correctly concatenates ALL of a
    node's descendant text into one string, avoiding the text-node-order
    problem.
    """
    xpath = (
        "//span[not(*)]"
        "[contains("
        "translate(normalize-space(string(.)), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
        "'download')]"
    )
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        print(f"[meta_scraper] Found {len(elements)} candidate span(s) matching 'download'")
        if not elements:
            return False

        el = elements[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", el)
        print(f"[meta_scraper] Clicked download element: {el.text!r} (tag: {el.tag_name})")
        return True
    except Exception as e:
        print(f"[meta_scraper] Could not find/click Download button: {e}")
        # Safety net: dump the full rendered page so we can grep it directly
        # for ground truth, instead of another screenshot-and-guess round trip.
        try:
            debug_path = OUTPUT_DIR / "_debug_page_source.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[meta_scraper] Saved full page HTML for debugging to: {debug_path}")
        except Exception as dump_err:
            print(f"[meta_scraper] Could not even save debug HTML: {dump_err}")
        return False


def wait_for_new_download(before_files: set, timeout: int = DOWNLOAD_WAIT_TIMEOUT) -> Path:
    """
    Poll the download folder until a new .csv OR .zip file appears and
    finishes writing. Meta actually packages the export as a ZIP (confirmed
    by a real run: 'community-standards.zip'), not a raw CSV — so both
    extensions are watched for, in case that changes in future.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        current_files = set(DOWNLOAD_DIR.glob("*.csv")) | set(DOWNLOAD_DIR.glob("*.zip"))
        new_files = current_files - before_files
        new_files = {f for f in new_files if not f.name.endswith(".crdownload")}
        if new_files:
            candidate = new_files.pop()
            size_before = candidate.stat().st_size
            time.sleep(1)
            if candidate.exists() and candidate.stat().st_size == size_before:
                return candidate
        time.sleep(1)

    all_files = list(DOWNLOAD_DIR.iterdir())
    print(f"[meta_scraper] DEBUG — contents of {DOWNLOAD_DIR} at timeout: "
          f"{[f.name for f in all_files] if all_files else '(empty)'}")
    raise TimeoutError(f"No new CSV/ZIP appeared in {DOWNLOAD_DIR} within {timeout}s")


def extract_csv_from_download(downloaded_path: Path) -> Path:
    """
    If the download is a ZIP, extract it and return the path to the CSV
    inside (preferring the largest .csv file if there happen to be several).
    If it's already a CSV, just return it unchanged.
    """
    if downloaded_path.suffix.lower() == ".csv":
        return downloaded_path

    if downloaded_path.suffix.lower() == ".zip":
        extract_dir = downloaded_path.parent / (downloaded_path.stem + "_extracted")
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(downloaded_path, "r") as zf:
            zf.extractall(extract_dir)

        csv_files = list(extract_dir.rglob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(
                f"ZIP downloaded but no .csv file found inside it: {downloaded_path}"
            )
        # If multiple CSVs are bundled, take the largest — most likely the
        # main dataset rather than a small metadata/readme file.
        largest_csv = max(csv_files, key=lambda p: p.stat().st_size)
        print(f"[meta_scraper] Extracted {len(csv_files)} CSV(s) from ZIP, "
              f"using largest: {largest_csv.name}")
        return largest_csv

    raise ValueError(f"Unexpected download file type: {downloaded_path}")


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Clear the download folder before starting. Without this, a leftover
    # file from a previous run (same filename, since Meta always calls it
    # "community-standards.zip") makes the "is this new?" check below
    # silently think nothing new arrived, because that filename already
    # existed in the "before" snapshot — this is exactly what happened on
    # the previous run.
    if DOWNLOAD_DIR.exists():
        shutil.rmtree(DOWNLOAD_DIR)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    driver = build_driver()
    try:
        print(f"[meta_scraper] Fetching overview: {OVERVIEW_URL}")
        driver.get(OVERVIEW_URL)
        wait_for_render(driver)

        before_files = set(DOWNLOAD_DIR.glob("*.csv")) | set(DOWNLOAD_DIR.glob("*.zip"))

        clicked = click_download_csv(driver)
        if not clicked:
            print("[meta_scraper] ABORTING — could not trigger the download click.")
            return

        print("[meta_scraper] Waiting for download...")
        downloaded_path = wait_for_new_download(before_files)
        print(f"[meta_scraper] Downloaded: {downloaded_path}")

        csv_path = extract_csv_from_download(downloaded_path)
        print(f"[meta_scraper] Using CSV: {csv_path}")

    finally:
        driver.quit()

    # Copy into data/raw/ with a clear, timestamped, permanent name
    final_path = OUTPUT_DIR / f"meta_cser_export_{timestamp}.csv"
    shutil.copy(csv_path, final_path)
    print(f"[meta_scraper] Saved permanent copy to: {final_path}")

    # Basic validation / sanity check using pandas
    df = pd.read_csv(final_path)
    print(f"\n[meta_scraper] Rows: {len(df)}")
    print(f"[meta_scraper] Columns: {list(df.columns)}")
    if "app" in df.columns:
        print(f"[meta_scraper] Apps present: {df['app'].unique().tolist()}")
        print(f"[meta_scraper] Row counts per app:\n{df['app'].value_counts()}")
    else:
        print("[meta_scraper] WARNING: no 'app' column found — check column names above, "
              "they may differ slightly from what we saw in the manual download.")


if __name__ == "__main__":
    run()
