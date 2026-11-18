#!/usr/bin/env python3
"""
Executable worked example for Website Cloner (index.html).

Demonstrates and verifies complete request-to-cloned-website pipeline:
  Step 1: HTML Form submission payload simulation (smallest and ordinary inputs)
  Step 2: POST parameter parsing
  Step 3: URL normalization
  Step 4: Destination folder resolution
  Step 5: Webpage archive generation
  Step 6: HTTP 301 redirection header calculation

Every intermediate state is asserted and logged.
"""

import os
import sys
import tempfile
import urllib.parse
from unittest.mock import MagicMock


def parse_form_post_data(post_body: str) -> str:
    """Step 2: Parse form submission data for submitButton parameter."""
    parsed = urllib.parse.parse_qs(post_body)
    return parsed.get("submitButton", [""])[0]


def normalize_clone_url(raw_url: str) -> str:
    """Step 3: Normalize raw input into HTTPS target URL."""
    cleaned = raw_url.strip("/")
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    return "https://" + cleaned


def resolve_project_folder(base_dir: str, raw_url: str) -> tuple[str, str]:
    """Step 4: Resolve sanitized folder path and project name."""
    project_name = raw_url.replace("https://", "").replace("http://", "").strip("/")
    folder_path = os.path.join(base_dir, "cloned_sites", project_name)
    return folder_path, project_name


def execute_clone_pipeline(raw_url_input: str, base_dir: str, mock_save_func=None) -> dict:
    """
    Execute and trace all intermediate stages of the Website Cloner pipeline.
    """
    # Stage 1: Form URL-encoded representation
    encoded_payload = urllib.parse.urlencode({"submitButton": raw_url_input})

    # Stage 2: Form parameter extraction
    extracted_url = parse_form_post_data(encoded_payload)
    assert extracted_url == raw_url_input, "Stage 2: Extracted URL must match input"

    # Stage 3: Normalization
    normalized_url = normalize_clone_url(extracted_url)
    assert normalized_url.startswith("https://") or normalized_url.startswith("http://"), "Stage 3: Protocol must be present"

    # Stage 4: Folder resolution
    project_folder, project_name = resolve_project_folder(base_dir, extracted_url)
    os.makedirs(project_folder, exist_ok=True)
    assert os.path.isdir(project_folder), "Stage 4: Destination folder must exist"

    # Stage 5: Webpage archive invocation
    if mock_save_func is not None:
        mock_save_func(url=normalized_url, project_folder=project_folder, project_name=project_name)
    else:
        # Create representative index.html in project folder
        with open(os.path.join(project_folder, "index.html"), "w") as f:
            f.write(f"<html><head><title>Cloned: {project_name}</title></head><body>Cloned content</body></html>")

    cloned_index_path = os.path.join(project_folder, "index.html")
    assert os.path.isfile(cloned_index_path), "Stage 5: Cloned index.html must exist"

    # Stage 6: HTTP 301 Location calculation
    relative_path = os.path.relpath(cloned_index_path, base_dir)
    redirect_location = "/" + relative_path.replace("\\", "/")

    return {
        "raw_input": raw_url_input,
        "encoded_payload": encoded_payload,
        "extracted_url": extracted_url,
        "normalized_url": normalized_url,
        "project_folder": project_folder,
        "project_name": project_name,
        "cloned_index_path": cloned_index_path,
        "redirect_location": redirect_location,
    }


def run_worked_examples():
    with tempfile.TemporaryDirectory() as tmpdir:
        print("=== Running Website Cloner Worked Example ===")

        # Example 1: Smallest valid input (bare domain)
        small_input = "example.com"
        print(f"\n[Example 1 - Smallest Valid Input]: '{small_input}'")
        res_small = execute_clone_pipeline(small_input, tmpdir)
        print(f"  Stage 1 (Payload):    {res_small['encoded_payload']}")
        print(f"  Stage 2 (Extracted):  {res_small['extracted_url']}")
        print(f"  Stage 3 (Normalized): {res_small['normalized_url']}")
        print(f"  Stage 4 (Folder):     {res_small['project_folder']}")
        print(f"  Stage 5 (Archived):   {res_small['cloned_index_path']}")
        print(f"  Stage 6 (Redirect):   {res_small['redirect_location']}")
        assert res_small["normalized_url"] == "https://example.com"
        assert res_small["project_name"] == "example.com"
        assert res_small["redirect_location"] == "/cloned_sites/example.com/index.html"
        print("  -> PASS: All intermediate stages verified for smallest input")

        # Example 2: Ordinary valid input (full URL)
        ord_input = "https://www.python.org"
        print(f"\n[Example 2 - Ordinary Valid Input]: '{ord_input}'")
        res_ord = execute_clone_pipeline(ord_input, tmpdir)
        print(f"  Stage 1 (Payload):    {res_ord['encoded_payload']}")
        print(f"  Stage 2 (Extracted):  {res_ord['extracted_url']}")
        print(f"  Stage 3 (Normalized): {res_ord['normalized_url']}")
        print(f"  Stage 4 (Folder):     {res_ord['project_folder']}")
        print(f"  Stage 5 (Archived):   {res_ord['cloned_index_path']}")
        print(f"  Stage 6 (Redirect):   {res_ord['redirect_location']}")
        assert res_ord["normalized_url"] == "https://www.python.org"
        assert res_ord["project_name"] == "www.python.org"
        assert res_ord["redirect_location"] == "/cloned_sites/www.python.org/index.html"
        print("  -> PASS: All intermediate stages verified for ordinary input")

    print("\nPASS: Runnable example executed successfully with all state invariants verified.")
    return 0


if __name__ == "__main__":
    sys.exit(run_worked_examples())
