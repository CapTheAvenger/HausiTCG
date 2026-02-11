#!/usr/bin/env python3
"""Test script to find working tournaments."""

import urllib.request
import urllib.error
import re
import sys

def fetch_page(url):
    """Fetch a web page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {url}")
        return None
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None

def test_tournament(tournament_id):
    """Test if a tournament has any decks."""
    url = f"https://labs.limitlesstcg.com/{tournament_id}/standings"
    print(f"\nTesting tournament {tournament_id}...", end=" ")
    html = fetch_page(url)
    if not html:
        return False
    
    # Check if page has deck data
    if '/player/' in html and '/decklist' in html:
        print("✓ Has deck links")
        return True
    else:
        print("✗ No deck links")
        return False

# Get list of tournaments
print("Fetching tournament list...")
html = fetch_page("https://labs.limitlesstcg.com/")
if html:
    matches = re.findall(r'/(\d+)/standings', html)
    tournament_ids = sorted(list(set(matches)), key=lambda x: int(x), reverse=True)
    print(f"Found {len(tournament_ids)} tournaments: {tournament_ids[:10]}...")
    
    working_tournaments = []
    for tournament_id in tournament_ids[:20]:  # Test first 20
        if test_tournament(tournament_id):
            working_tournaments.append(tournament_id)
    
    if working_tournaments:
        print(f"\n✓ Working tournaments: {working_tournaments}")
    else:
        print("\n✗ No working tournaments found")
else:
    print("Failed to fetch tournament list")
