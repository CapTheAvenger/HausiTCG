#!/usr/bin/env python3
"""
Unified Card Scraper
Combines City League, Limitless Online, and Tournament data
Aggregates card usage with set/number info and archetype percentages
No external dependencies - uses only Python standard library
"""

import urllib.request
import urllib.parse
import csv
import re
import time
import json
import os
import sys
from datetime import datetime
from html.parser import HTMLParser
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

# Import dedicated scrapers - try to load them
_city_league_available = False
_limitless_available = False

try:
    # Try importing from standard path first
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import city_league_archetype_scraper as city_league_module
    _city_league_available = True
    print("[DEBUG] City League module imported successfully")
except Exception as e:
    city_league_module = None
    print(f"[DEBUG] City League import failed: {type(e).__name__}: {e}")

try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import limitless_online_scraper as limitless_module
    _limitless_available = True
    print("[DEBUG] Limitless Online module imported successfully")
except Exception as e:
    limitless_module = None
    print(f"[DEBUG] Limitless Online import failed: {type(e).__name__}: {e}")

# Import card type lookup
try:
    from card_type_lookup import is_trainer_or_energy, is_valid_card
except ImportError:
    # Fallback if module not available
    def is_trainer_or_energy(card_name: str) -> bool:
        """Fallback trainer/energy detection."""
        trainer_keywords = ['Professor', 'Boss', 'Ball', 'Rod', 'Switch', 'Candy', 'Belt', 
                           'Poffin', 'Nest', 'Ultra', 'Search', 'Town', 'Iono', 'Arven',
                           'Colress', 'Stadium', 'Pokédex', 'Energy', 'Reversal']
        return any(keyword in card_name for keyword in trainer_keywords)
    
    def is_valid_card(card_name: str) -> bool:
        """Fallback card validation."""
        return len(card_name) > 0

# Default settings
DEFAULT_SETTINGS: Dict[str, Any] = {
    "sources": {
        "city_league": {
            "enabled": True,
            "start_date": "24.01.2026",  # Fixed start date in 'DD.MM.YYYY' format
            "end_date": "auto",           # 'auto' = today - 2 days, or use 'DD.MM.YYYY'
            "max_decklists_per_league": 16  # 0 = all decklists
        },
        "limitless_online": {
            "enabled": True,
            "game": "POKEMON",
            "format": "STANDARD",
            "rotation": "2025",
            "set": "PFL",
            "top_decks": 20,
            "max_lists_per_deck": 5
        },
        "tournaments": {
            "enabled": True,
            "max_tournaments": 5,
            "max_decks_per_tournament": 128,
            "format_filter": ["Standard", "Standard (JP)"]
        }
    },
    "delay_between_requests": 1.5,
    "output_file": "unified_card_data.csv"
}

def get_app_path() -> str:
    """Get the directory where the executable/script is located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_data_dir() -> str:
    """Get the shared data directory for CSV outputs."""
    app_path = get_app_path()
    
    # If running from dist/[scraper_name]/, go up two levels to workspace root
    # If running from scripts/, go up one level to workspace root
    parts = app_path.replace('\\', '/').split('/')
    
    # Check if we're in a scraper folder inside dist
    if 'dist' in parts:
        dist_index = parts.index('dist')
        base_path = '/'.join(parts[:dist_index])  # Everything before 'dist'
    elif parts[-1] == 'scripts':
        base_path = '/'.join(parts[:-1])  # Everything except 'scripts'
    else:
        base_path = app_path
    
    return os.path.join(base_path, 'data')

def calculate_date_range(start_date: str, end_date: str) -> Tuple[str, str]:
    """Calculate date range for scraping.
    
    Args:
        start_date: Fixed date in 'DD.MM.YYYY' format
        end_date: 'auto' for today-2, or 'DD.MM.YYYY'
    
    Returns:
        Tuple of (start_date, end_date) in 'DD.MM.YYYY' format
    """
    from datetime import datetime, timedelta
    
    # Start date is always provided as fixed date
    start_str = start_date
    
    # Calculate end_date if 'auto'
    if end_date == 'auto':
        # Today - 2 days
        end_dt = datetime.now() - timedelta(days=2)
        end_str = end_dt.strftime('%d.%m.%Y')
    else:
        # Use provided date
        end_str = end_date
    
    return start_str, end_str

def load_settings() -> Dict[str, Any]:
    """Load settings from unified_card_settings.json."""
    app_path = get_app_path()
    settings_path = os.path.join(app_path, 'unified_card_settings.json')
    
    if not os.path.exists(settings_path) and os.path.basename(app_path) == 'dist':
        parent_path = os.path.dirname(app_path)
        settings_path = os.path.join(parent_path, 'unified_card_settings.json')
    
    print(f"Loading settings from: {settings_path}")
    
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                # Debug: show first 500 chars of file
                print(f"[DEBUG] Settings file content (first 300 chars): {content[:300]}")
                settings = json.loads(content)
                print(f"Settings loaded successfully")
                # Debug: show loaded structure
                print(f"[DEBUG] Loaded settings keys: {list(settings.keys())}")
                if 'sources' in settings:
                    print(f"[DEBUG] Sources keys: {list(settings.get('sources', {}).keys())}")
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            import traceback
            traceback.print_exc()
            return DEFAULT_SETTINGS.copy()
    else:
        print(f"Creating default settings file...")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS.copy()

def fetch_page(url: str) -> str:
    """Fetch a webpage and return its HTML content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""

# ============================================================================
# CARD DATABASE LOOKUP (from all_cards_database.csv)
# ============================================================================

class CardDatabaseLookup:
    """Lookup card information from local CSV database."""
    
    # Rarity priority (lower = better) - LOW RARITY preferred!
    RARITY_PRIORITY = {
        'Common': 1,
        'Uncommon': 2,
        'Double Rare': 3,
        'Rare': 4,
        'Art Rare': 20,  # Mid Rarity - much lower priority
        'Ultra Rare': 21,  # Mid Rarity - much lower priority
        'Secret Rare': 30,  # High Rarity - lowest priority
        'Special Illustration Rare': 31,  # High Rarity - lowest priority
        'Hyper Rare': 32,  # High Rarity - lowest priority
        'Illustration Rare': 33,
        'Promo': 5  # Promo cards can be low rarity
    }
    
    # Set order priority (higher = newer/better) - LATEST sets first!
    # ASC (Scarlet ex) is newer than MEG (Scarlet & Violet base), so ASC has higher priority
    SET_ORDER = {
        'PRE': 102, 'SFA': 101, 'ASC': 101, 'MEG': 100, 'MEP': 99, 'SP': 99, 'SVE': 98,
        'SCR': 98, 'SSH': 97, 'MEW': 96, 'BLK': 95, 'SSP': 94, 'SVI': 93, 'TEF': 92,
        'TWM': 91, 'PAR': 90, 'PAF': 89, 'PAL': 89, 'OBF': 88, 'PR-SW': 87, 'SVP': 86,
        'CRZ': 85, 'SIT': 84, 'LOR': 83, 'PGO': 82, 'ASR': 81, 'BRS': 80, 'FST': 79,
        'CEL': 78, 'EVS': 77, 'CRE': 76, 'BST': 75, 'SHF': 74, 'VIV': 73, 'CPA': 72,
        'DAA': 71, 'RCL': 70, 'MP1': 50, 'M3': 20, 'MC': 15, 'JTG': 10, 'PFL': 5, 'DRI': 2
    }
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.cards: Dict[str, List[Dict[str, str]]] = {}  # name -> list of card variants
        self.load_database()
    
    def normalize_name(self, name: str) -> str:
        """Normalize card name for matching."""
        normalized = name.strip().lower()
        normalized = normalized.replace("'", "'").replace("'", "'").replace("`", "'")
        normalized = normalized.replace('-', ' ').replace('.', '')
        normalized = ' '.join(normalized.split())
        return normalized
    
    def load_database(self):
        """Load all cards from CSV database."""
        if not os.path.exists(self.csv_path):
            print(f"⚠️  Warning: Card database not found at {self.csv_path}")
            return
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                count = 0
                for row in reader:
                    # Try both column name formats
                    card_name = row.get('name', row.get('Name', '')).strip()
                    if not card_name:
                        continue
                    
                    normalized = self.normalize_name(card_name)
                    
                    card_info = {
                        'name': card_name,
                        'set_code': row.get('set', row.get('Set Code', '')),
                        'set_number': row.get('number', row.get('Number', '')),
                        'rarity': row.get('rarity', row.get('Rarity', '')),
                        'type': row.get('type', row.get('Type', '')),
                        'card_type': row.get('card_type', row.get('Card Type', '')) or row.get('type', row.get('Type', 'Pokemon'))
                    }
                    
                    if normalized not in self.cards:
                        self.cards[normalized] = []
                    self.cards[normalized].append(card_info)
                    count += 1
                
                print(f"Loaded {count} cards from database ({len(self.cards)} unique names)")
        except Exception as e:
            print(f"Error loading card database: {e}")
    
    def is_card_trainer_or_energy(self, variants: List[Dict[str, str]]) -> bool:
        """Check if this card is a Trainer or Energy card based on type/card_type from database."""
        if not variants:
            return False
        # Check the first variant - they should all be same type
        card_type = variants[0].get('card_type', '') or variants[0].get('type', '')
        card_type_lower = card_type.lower()
        return 'trainer' in card_type_lower or 'supporter' in card_type_lower or 'energy' in card_type_lower or 'stadium' in card_type_lower or 'tool' in card_type_lower

    def is_card_trainer_or_energy_by_name(self, card_name: str) -> bool:
        """Check if a card (by name) is a Trainer or Energy card."""
        normalized = self.normalize_name(card_name)
        if normalized in self.cards:
            return self.is_card_trainer_or_energy(self.cards[normalized])
        return False

    def generate_limitless_image_url(self, set_code: str, card_number: str, rarity: str) -> str:
        """Generate Limitless CDN image URL for EN or JP cards."""
        set_code = set_code.upper()
        card_number = card_number.replace('-', '_')
        # Pad card number to 3 digits with leading zeros (e.g., 54 -> 054)
        card_number = card_number.lstrip('0') or '0'  # Remove leading zeros first
        card_number = card_number.zfill(3)  # Pad to 3 digits
        rarity = rarity.upper()

        # Determine if Japanese or English
        is_japanese = any(char.isdigit() for char in set_code)
        
        # For ALL cards (English & Japanese): always use R
        # The Limitless CDN image links always use R for the rarity placeholder
        # regardless of the actual card rarity
        rarity_short = 'R'

        base_path = 'tpc' if is_japanese else 'tpci'
        language = 'JP' if is_japanese else 'EN'

        return (
            f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/{base_path}/"
            f"{set_code}/{set_code}_{card_number}_{rarity_short}_{language}_LG.png"
        )
    
    def get_card_info(self, card_name: str) -> Optional[Dict[str, str]]:
        """Get card info.
        
        For Trainer/Energy cards: Use NEWEST set (ASC > MEG > BRS...) regardless of rarity
        For Pokemon cards: Use LOWEST rarity (Common > Uncommon) regardless of set
        """
        normalized = self.normalize_name(card_name)
        
        # Try exact match first
        if normalized in self.cards:
            variants = self.cards[normalized]
            
            # Determine if this is a Trainer/Energy card
            is_trainer_energy = self.is_card_trainer_or_energy(variants)
            
            best_card = None
            best_priority = 999
            best_set_order = -1
            
            for variant in variants:
                set_order = self.SET_ORDER.get(variant['set_code'], 0)
                
                if is_trainer_energy:
                    # For Trainer/Energy: Prefer NEWEST set only
                    if set_order > best_set_order:
                        best_card = variant
                        best_set_order = set_order
                else:
                    # For Pokemon: Prefer LOWEST rarity, then NEWEST set
                    rarity = variant['rarity']
                    priority = self.RARITY_PRIORITY.get(rarity, 50)
                    if priority < best_priority or (priority == best_priority and set_order > best_set_order):
                        best_card = variant
                        best_priority = priority
                        best_set_order = set_order
            
            if best_card:
                image_url = self.generate_limitless_image_url(
                    best_card['set_code'],
                    best_card['set_number'],
                    best_card['rarity']
                )
                
                return {
                    'set_code': best_card['set_code'],
                    'set_name': '',  # Not in CSV
                    'number': best_card['set_number'],
                    'rarity': best_card['rarity'],
                    'image_url': image_url
                }
        
        # Try partial match (for cards with ex/V suffixes or truncated names)
        # First try: cards where input is contained in database name
        for db_name, variants in self.cards.items():
            if normalized in db_name:
                # Determine if this is a Trainer/Energy card
                is_trainer_energy = self.is_card_trainer_or_energy(variants)
                
                best_card = None
                best_priority = 999
                best_set_order = -1
                
                for variant in variants:
                    set_order = self.SET_ORDER.get(variant['set_code'], 0)
                    
                    if is_trainer_energy:
                        # For Trainer/Energy: Prefer NEWEST set only
                        if set_order > best_set_order:
                            best_card = variant
                            best_set_order = set_order
                    else:
                        # For Pokemon: Prefer LOWEST rarity, then NEWEST set
                        rarity = variant['rarity']
                        priority = self.RARITY_PRIORITY.get(rarity, 50)
                        if priority < best_priority or (priority == best_priority and set_order > best_set_order):
                            best_card = variant
                            best_priority = priority
                            best_set_order = set_order
                
                if best_card:
                    image_url = self.generate_limitless_image_url(
                        best_card['set_code'],
                        best_card['set_number'],
                        best_card['rarity']
                    )
                    
                    return {
                        'set_code': best_card['set_code'],
                        'set_name': '',
                        'number': best_card['set_number'],
                        'rarity': best_card['rarity'],
                        'image_url': image_url
                    }
        
        # Second try: database name is contained in input (for cases where scraped name is longer)
        for db_name, variants in self.cards.items():
            if db_name in normalized and len(db_name) > 3:  # Only if db_name is meaningful length
                # Determine if this is a Trainer/Energy card
                is_trainer_energy = self.is_card_trainer_or_energy(variants)
                
                best_card = None
                best_priority = 999
                best_set_order = -1
                
                for variant in variants:
                    set_order = self.SET_ORDER.get(variant['set_code'], 0)
                    
                    if is_trainer_energy:
                        # For Trainer/Energy: Prefer NEWEST set only
                        if set_order > best_set_order:
                            best_card = variant
                            best_set_order = set_order
                    else:
                        # For Pokemon: Prefer LOWEST rarity, then NEWEST set
                        rarity = variant['rarity']
                        priority = self.RARITY_PRIORITY.get(rarity, 50)
                        if priority < best_priority or (priority == best_priority and set_order > best_set_order):
                            best_card = variant
                            best_priority = priority
                            best_set_order = set_order
                
                if best_card:
                    image_url = self.generate_limitless_image_url(
                        best_card['set_code'],
                        best_card['set_number'],
                        best_card['rarity']
                    )
                    
                    return {
                        'set_code': best_card['set_code'],
                        'set_name': '',
                        'number': best_card['set_number'],
                        'rarity': best_card['rarity'],
                        'image_url': image_url
                    }
        
        return None
    
    def get_card_info_by_set_number(self, card_name: str, set_code: str, card_number: str) -> Optional[Dict[str, str]]:
        """Get card info for a specific set and number.
        
        For Pokemon cards: Return the exact card from the specified set/number
        For Trainer/Energy: Return the exact card from the specified set/number
        
        This preserves the original card selection from the source (Limitless/Tournament)
        without re-selecting based on rarity or set order.
        """
        # Normalize card name for lookup
        normalized = self.normalize_name(card_name)
        
        if normalized not in self.cards:
            return None
        
        variants = self.cards[normalized]
        
        # Find the exact variant matching the set and number
        for variant in variants:
            if variant['set_code'] == set_code and variant['set_number'] == card_number:
                image_url = self.generate_limitless_image_url(set_code, card_number, variant['rarity'])
                return {
                    'set_code': variant['set_code'],
                    'set_name': '',
                    'number': variant['set_number'],
                    'rarity': variant['rarity'],
                    'image_url': image_url
                }
        
        return None
    
    def get_name_by_set_number(self, set_code: str, card_number: str) -> Optional[str]:
        """Lookup card name by set code and number."""
        if not set_code or not card_number:
            return None

        normalized_set = set_code.strip().upper()
        normalized_number = card_number.strip().lstrip('0') or card_number.strip()
        
        # Search through all cards for matching set+number
        for db_name, variants in self.cards.items():
            for variant in variants:
                variant_set = (variant['set_code'] or '').strip().upper()
                variant_number = (variant['set_number'] or '').strip()
                variant_number_norm = variant_number.lstrip('0') or variant_number

                if variant_set == normalized_set and (
                    variant_number == card_number.strip() or variant_number_norm == normalized_number
                ):
                    return variant['name']
        
        return None

def normalize_archetype_name(archetype: str) -> str:
    """Normalize archetype names to consistent Title Case format.
    
    This ensures "alakazam dragapult", "Alakazam Dragapult", and "ALAKAZAM DRAGAPULT" 
    all become "Alakazam Dragapult" for consistency.
    """
    name = archetype.strip()
    
    # Convert to Title Case (first letter of each word capitalized)
    name = name.title()
    
    # ONLY remove single-letter prefixes that are trainer names (N's Zoroark)
    name = re.sub(r'^N\s+', '', name, flags=re.IGNORECASE)   # "N Zoroark" -> "Zoroark"
    name = re.sub(r'^Ns\s+', '', name, flags=re.IGNORECASE)  # "Ns Zoroark" -> "Zoroark"
    
    # DO NOT remove Ex/V/Vstar/Vmax - these are important variant markers
    # DO NOT remove 3-letter words - could be partner Pokemon names (Meg = Mega Diance)
    
    return name.strip()

# ============================================================================
# CARD INFO LOOKUP
# Note: Card database (CardDatabaseLookup) is now the primary method for
# card lookups. The old Pokemon TCG API integration has been removed.
# ============================================================================

# ============================================================================
# CITY LEAGUE SCRAPER
# ============================================================================

class CityLeagueParser(HTMLParser):
    """Parser for City League tournament pages."""
    def __init__(self):
        super().__init__()
        self.decks = []
        self.in_deck_list = False
        self.current_deck = None
        self.current_tag = None
        self.current_count = None
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'div' and attrs_dict.get('class') == 'decklist':
            self.in_deck_list = True
            self.current_deck = {'archetype': '', 'cards': []}
        
        if self.in_deck_list:
            if tag == 'h3':
                self.current_tag = 'archetype'
            elif tag == 'span' and 'quantity' in attrs_dict.get('class', ''):
                self.current_tag = 'quantity'
            elif tag == 'a' and 'card-link' in attrs_dict.get('class', ''):
                self.current_tag = 'card'
    
    def handle_data(self, data):
        if self.in_deck_list:
            if self.current_tag == 'archetype':
                self.current_deck['archetype'] = data.strip()
                self.current_tag = None
            elif self.current_tag == 'quantity':
                self.current_count = int(data.strip())
                self.current_tag = None
            elif self.current_tag == 'card':
                card_name = data.strip()
                if self.current_count and is_valid_card(card_name):
                    self.current_deck['cards'].append({
                        'name': card_name,
                        'count': self.current_count
                    })
                self.current_count = None
                self.current_tag = None
    
    def handle_endtag(self, tag):
        if tag == 'div' and self.in_deck_list and self.current_deck:
            if self.current_deck['archetype'] and self.current_deck['cards']:
                self.decks.append(self.current_deck)
            self.current_deck = None
            self.in_deck_list = False

def scrape_city_league(settings: Dict[str, Any], card_db: CardDatabaseLookup) -> List[Dict[str, Any]]:
    """Scrape City League tournament data using city_league_archetype_scraper module."""
    print("\n" + "="*60)
    print("SCRAPING CITY LEAGUE DATA")
    print("="*60)
    
    # Debug: check module availability
    print(f"[DEBUG] _city_league_available: {_city_league_available}")
    print(f"[DEBUG] city_league_module is None: {city_league_module is None}")
    
    if not _city_league_available or not city_league_module:
        print("❌ City League module not available - skipping")
        return []
    
    config = settings.get('sources', {}).get('city_league', {})
    print(f"[DEBUG] Config: {config}")
    print(f"[DEBUG] Config enabled: {config.get('enabled', False)}")
    
    if not config.get('enabled', False):
        print("⚠️  City League disabled in settings - skipping")
        return []
    
    all_decks = []
    
    try:
        start_date_str = config.get('start_date', '24.01.2026')
        end_date_str = config.get('end_date', 'auto')
        max_decklists = config.get('max_decklists_per_league', 16)
        
        print(f"📅 Start date: {start_date_str}, End date: {end_date_str}")
        print(f"📊 Max decklists per league: {max_decklists}")
        
        # Calculate date range
        start_date, end_date = calculate_date_range(start_date_str, end_date_str)
        
        print(f"Scraping City League tournaments from {start_date} to {end_date}")
        
        # Parse dates
        from datetime import datetime
        start_dt = datetime.strptime(start_date, "%d.%m.%Y")
        end_dt = datetime.strptime(end_date, "%d.%m.%Y")
        
        # Get tournaments (JP region is where City League is)
        print("🔍 Fetching tournaments...")
        tournaments = city_league_module.get_tournaments_in_date_range(
            "jp", start_dt, end_dt, 1.5
        )
        
        print(f"✓ Found {len(tournaments)} City League tournaments")
        
        if not tournaments:
            print("⚠️  No tournaments found in date range")
            return []
        
        for i, tournament in enumerate(tournaments, 1):
            print(f"\n  [{i}/{len(tournaments)}] {tournament.get('date_str', 'Unknown date')}")
            
            # Scrape this tournament
            archetypes = city_league_module.scrape_tournament_archetypes(
                tournament['url'],
                tournament,
                1.5
            )
            
            print(f"  Found {len(archetypes)} archetypes")
            
            # Extract individual deck lists (limit per league if configured)
            if max_decklists > 0:
                archetypes = archetypes[:max_decklists]
            
            all_decks.extend(archetypes)
        
        print(f"\n✓ Collected {len(all_decks)} total deck entries from City League")
        
    except Exception as e:
        import traceback
        print(f"❌ Error scraping City League: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
    
    return all_decks
    
    return all_decks

# ============================================================================
# LIMITLESS ONLINE SCRAPER
# ============================================================================

def scrape_limitless_online(settings: Dict[str, Any], card_db: CardDatabaseLookup) -> List[Dict[str, Any]]:
    """Scrape Limitless Online deck data using limitless_online_scraper module."""
    print("\n" + "="*60)
    print("SCRAPING LIMITLESS ONLINE DATA")
    print("="*60)
    
    # Debug: check module availability
    print(f"[DEBUG] _limitless_available: {_limitless_available}")
    print(f"[DEBUG] limitless_module is None: {limitless_module is None}")
    
    if not _limitless_available or not limitless_module:
        print("❌ Limitless Online module not available - skipping")
        return []
    
    config = settings.get('sources', {}).get('limitless_online', {})
    print(f"[DEBUG] Config: {config}")
    print(f"[DEBUG] Config enabled: {config.get('enabled', False)}")
    
    if not config.get('enabled', False):
        print("⚠️  Limitless Online disabled in settings - skipping")
        return []
    
    all_decks = []
    
    try:
        max_decks = config.get('max_decks', 150)
        max_lists_per_deck = config.get('max_lists_per_deck', 20)
        format_filter = config.get('format_filter', 'PFL')
        
        print(f"📊 Max decks: {max_decks}, Max lists per deck: {max_lists_per_deck}")
        print(f"🎯 Format filter: {format_filter}")
        
        # Get deck statistics from Limitless Online
        print("🔍 Fetching deck statistics...")
        deck_stats = limitless_module.scrape_deck_statistics(
            game="POKEMON",
            format_type="STANDARD",
            rotation="2025",
            set_code=format_filter
        )
        
        print(f"✓ Found {len(deck_stats)} decks from Limitless Online")
        
        # Limit to max_decks
        deck_stats = deck_stats[:max_decks]
        print(f"📋 Processing top {len(deck_stats)} decks")
        
        if not deck_stats:
            print("⚠️  No decks found")
            return []
        
        # Scrape individual deck lists
        for i, deck in enumerate(deck_stats, 1):
            deck_name = deck.get('deck_name', 'Unknown')
            deck_url = deck.get('url', '')
            
            if not deck_url:
                print(f"  ⚠️  [{i}/{len(deck_stats)}] {deck_name} - No URL found, skipping")
                continue
            
            print(f"  [{i}/{len(deck_stats)}] {deck_name}")
            
            try:
                # Get matchup data which contains individual lists
                matchup_data = limitless_module.scrape_matchup_data(
                    deck_url, "STANDARD", "2025", format_filter, 1.5
                )
                
                print(f"    Found {len(matchup_data)} lists")
                all_decks.extend(matchup_data[:max_lists_per_deck])
            except Exception as e:
                print(f"    ❌ Error scraping {deck_name}: {str(e)}")
                continue
        
        print(f"\n✓ Collected {len(all_decks)} total deck lists from Limitless Online")
        
    except Exception as e:
        import traceback
        print(f"❌ Error scraping Limitless Online: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
    
    return all_decks
    
    return all_decks

# ============================================================================
# TOURNAMENT SCRAPER
# ============================================================================

def get_tournament_links(base_url: str, max_tournaments: int) -> List[Dict[str, str]]:
    """Get tournament links from labs.limitlesstcg.com."""
    tournaments = []
    
    print(f"  Loading tournaments from {base_url}...")
    html = fetch_page(base_url)
    if not html:
        return []
    
    # Extract tournament IDs from links like /0050/standings
    matches = re.findall(r'href=["\']/(\d+)/standings["\']', html)
    seen_ids = set()
    
    for tournament_id in matches:
        if tournament_id not in seen_ids:
            seen_ids.add(tournament_id)
            tournaments.append({
                'id': tournament_id,
                'url': f'https://labs.limitlesstcg.com/{tournament_id}/standings',
                'standings_url': f'https://labs.limitlesstcg.com/{tournament_id}/standings'
            })
        
        if len(tournaments) >= max_tournaments:
            break
    
    result = tournaments[:max_tournaments]
    print(f"  Found {len(result)} tournaments")
    return result

def get_tournament_info(tournament_url: str) -> Dict[str, str]:
    """Get tournament name and details from the tournament page."""
    html = fetch_page(tournament_url)
    if not html:
        return {'name': 'Unknown Tournament', 'date': '', 'format': '', 'meta': 'Standard'}
    
    info = {'name': 'Unknown Tournament', 'date': '', 'format': ''}
    
    # Extract tournament name
    title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        title = re.sub(r'\s*\|\s*Limitless.*$', '', title)
        info['name'] = title
    
    # Extract date
    date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4})', html)
    if date_match:
        info['date'] = date_match.group(1)
    
    # Detect format and meta
    is_jp_tournament = False
    if 'Standard (JP)' in html or 'Champions League' in info.get('name', '') or 'Regional League' in info.get('name', ''):
        is_jp_tournament = True
    
    if is_jp_tournament:
        info['format'] = ''
        info['meta'] = 'Standard (JP)'
    elif 'Expanded' in html:
        info['meta'] = 'Expanded'
    else:
        info['meta'] = 'Standard'
    
    return info

def get_deck_links_from_standings(tournament_id: str, max_decks: int = 128) -> List[Dict[str, str]]:
    """Get deck links from tournament standings page."""
    standings_url = f"https://labs.limitlesstcg.com/{tournament_id}/standings"
    html = fetch_page(standings_url)
    if not html:
        return []
    
    deck_links = []
    
    # Strategy: Parse the HTML line by line to find player-archetype pairs
    # The HTML structure has rows like:
    # <tr>...player link.../0050/player/123/decklist...deck link.../0050/decks/alakazam-dudunsparce...</tr>
    
    # Split into table rows
    rows = re.split(r'<tr[^>]*>', html, flags=re.IGNORECASE)
    
    for row in rows:
        # Look for player decklist link
        player_match = re.search(r'href="/' + re.escape(tournament_id) + r'/player/(\d+)/decklist"', row)
        if not player_match:
            continue
        
        player_id = player_match.group(1)
        
        # Look for deck archetype link in the same row
        deck_match = re.search(r'href="/' + re.escape(tournament_id) + r'/decks/([^"]+)"', row)
        
        if deck_match:
            archetype_slug = deck_match.group(1)
            # Convert slug to readable name (e.g., "alakazam-dudunsparce" -> "Alakazam Dudunsparce")
            archetype = archetype_slug.replace('-', ' ').title()
        else:
            # No archetype link found - try to extract from text or default to Unknown
            archetype = "Unknown"
        
        deck_links.append({
            'player_id': player_id,
            'url': f"https://labs.limitlesstcg.com/{tournament_id}/player/{player_id}/decklist",
            'archetype': archetype
        })
        
        if len(deck_links) >= max_decks:
            break
    
    return deck_links[:max_decks]

def extract_cards_from_decklist(decklist_url: str) -> List[Dict[str, Any]]:
    """Extract card data from a player's decklist page on labs.limitlesstcg.com."""
    html_content = fetch_page(decklist_url)
    if not html_content:
        return []

    cards: List[Dict] = []
    
    # Labs.limitlesstcg.com stores deck data in JSON within script tags
    # Pattern: <script>{"status":200,...,"body":"{\"ok\":true,\"message\":{\"pokemon\":[...],\"trainer\":[...],\"energy\":[...]}}"}
    script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(html_content)
    
    for script in scripts:
        try:
            # Check if this script contains deck data (check for escaped quotes too)
            if 'pokemon' not in script.lower() and 'trainer' not in script.lower():
                continue
            
            # Parse the outer JSON
            data = json.loads(script)
            if 'body' not in data:
                continue
            
            # Parse the inner JSON (which is a string)
            body_data = json.loads(data['body'])
            if not body_data.get('ok') or 'message' not in body_data:
                continue
            
            message = body_data['message']
            
            # Extract cards from each category
            for category in ['pokemon', 'trainer', 'energy']:
                if category not in message:
                    continue
                
                for card in message[category]:
                    try:
                        count = int(card.get('count', 0))
                        name = card.get('name', '').strip()
                        
                        if not name or count == 0:
                            continue
                        
                        # Clean up name
                        import html as html_module
                        name = html_module.unescape(name)
                        name = name.replace("'", "'").replace("`", "'").replace("´", "'").replace("'", "'")
                        
                        cards.append({
                            'name': name,
                            'count': count,
                            'set_code': '',
                            'card_number': ''
                        })
                    except (ValueError, KeyError):
                        continue
            
            # If we found cards, we're done
            if cards:
                break
                
        except (json.JSONDecodeError, KeyError):
            continue
    
    return cards

def extract_cards_from_tournament(cards_url: str, deck_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extract card data from a tournament's cards page."""
    html_content = fetch_page(cards_url)
    if not html_content:
        return []

    cards: List[Dict] = []
    seen_cards = set()

    # Regex patterns
    heading_pattern = re.compile(r'<div[^>]*class="decklist-column-heading"[^>]*>\s*([^<]+?)\s*</div>', re.IGNORECASE)
    card_pattern = re.compile(r'<div[^>]*class="decklist-card"[^>]*data-set="([A-Z0-9]*)"[^>]*data-number="(\d*)"[^>]*>.*?<span class="card-count">([0-9.]+)</span>\s*<span class="card-name">([^<]+)</span>', re.IGNORECASE | re.DOTALL)

    # Find all headings
    headings = []
    for m in heading_pattern.finditer(html_content):
        title = m.group(1).strip().lower()
        if 'trainer' in title:
            section_type = 'trainer'
        elif 'energy' in title:
            section_type = 'energy'
        else:
            section_type = 'pokemon'
        headings.append({'start': m.end(), 'type': section_type})

    # Determine end positions
    for idx in range(len(headings)):
        start = headings[idx]['start']
        end = headings[idx + 1]['start'] if idx + 1 < len(headings) else len(html_content)
        headings[idx]['end'] = end

    # Extract cards per section
    import html as html_module
    for sec in headings if headings else [{'start': 0, 'end': len(html_content), 'type': 'pokemon'}]:
        block = html_content[sec['start']:sec['end']]
        section_type = sec['type']

        for match in card_pattern.findall(block):
            try:
                set_code_raw = match[0].upper() if match[0] else ""
                card_number_raw = match[1] if match[1] else ""
                count_str = match[2]
                name = match[3].strip()

                name = html_module.unescape(name)
                name = name.replace("'", "'").replace("`", "'").replace("´", "'").replace("'", "'")

                if not is_valid_card(name):
                    continue

                count = int(float(count_str) + 0.5)  # Round up

                # ALL cards get set/number info (Pokemon, Trainer, AND Energy!)
                set_code = set_code_raw if set_code_raw else ""
                card_number = card_number_raw if card_number_raw else ""
                if set_code == 'PR-SV':
                    set_code = 'SVP'
                
                # Create unique key with set/number for all cards
                if set_code and card_number:
                    card_key = f"{name}|{set_code}|{card_number}".lower()
                else:
                    card_key = name.lower()

                if card_key not in seen_cards and name:
                    seen_cards.add(card_key)
                    cards.append({
                        'name': name,
                        'count': count,
                        'set_code': set_code,
                        'card_number': card_number
                    })
                elif card_key in seen_cards and name:
                    # Card already exists, add to count
                    for existing_card in cards:
                        # Create same key format for comparison (all cards use set/number)
                        if existing_card.get('set_code') and existing_card.get('card_number'):
                            existing_key = f"{existing_card['name']}|{existing_card.get('set_code', '')}|{existing_card.get('card_number', '')}".lower()
                        else:
                            existing_key = existing_card['name'].lower()
                        
                        if existing_key == card_key:
                            existing_card['count'] += count
                            break
            except (ValueError, IndexError):
                continue

    return cards

def scrape_tournaments(settings: Dict[str, Any], card_db: CardDatabaseLookup) -> List[Dict[str, Any]]:
    """Scrape tournament deck data from labs.limitlesstcg.com - PRIMARY SOURCE for card lists."""
    print("\n" + "="*60)
    print("SCRAPING TOURNAMENT DATA (Complete Card Lists)")
    print("="*60)
    
    config = settings['sources']['tournaments']
    if not config.get('enabled'):
        print("Tournament scraping disabled in settings")
        return []
    
    max_tournaments = config.get('max_tournaments', 150)
    max_decks_per_tournament = config.get('max_decks_per_tournament', 128)
    
    base_url = "https://labs.limitlesstcg.com/"
    all_decks = []
    
    # Get tournament links
    tournaments = get_tournament_links(base_url, max_tournaments)
    if not tournaments:
        print("No tournaments found")
        return []
    
    for i, tournament in enumerate(tournaments, 1):
        print(f"\n[{i}/{len(tournaments)}] Processing tournament {tournament['id']}...")
        
        # Get tournament info
        info = get_tournament_info(tournament['url'])
        print(f"  {info['name']}")
        
        # Get deck links from standings
        deck_links = get_deck_links_from_standings(tournament['id'], max_decks_per_tournament)
        if not deck_links:
            print("  No decks found")
            continue
        
        print(f"  Found {len(deck_links)} decks, scraping...")
        
        for j, deck_info in enumerate(deck_links, 1):
            if j % 20 == 0:
                print(f"    Processed {j}/{len(deck_links)} decks...")
            
            cards = extract_cards_from_decklist(deck_info['url'])
            
            if cards:
                all_decks.append({
                    'archetype': normalize_archetype_name(deck_info['archetype']),
                    'cards': cards,
                    'source': 'Tournament'
                })
        
        print(f"  Collected {len(all_decks)} complete decks so far")
        time.sleep(settings.get('delay_between_requests', 1.0))
    
    print(f"\n✓ Total decks with FULL CARD LISTS from tournaments: {len(all_decks)}")
    return all_decks

# ============================================================================
# DATA AGGREGATION AND ANALYSIS
# ============================================================================

def aggregate_card_data(all_decks: List[Dict[str, Any]], card_db: CardDatabaseLookup) -> List[Dict[str, Any]]:
    """Aggregate card data from all sources with archetype percentages."""
    print("\n" + "="*60)
    print("AGGREGATING CARD DATA")
    print("="*60)
    
    # Structure: {archetype: {card_name: {'total_count': X, 'deck_count': Y, 'max_count': Z, 'decks': [], 'set_codes': {}}}}
    archetype_cards = defaultdict(lambda: defaultdict(lambda: {'total_count': 0, 'deck_count': 0, 'max_count': 0, 'decks': [], 'set_codes': {}}))
    archetype_deck_counts = defaultdict(int)  # Total decks per archetype (with cards)
    archetype_total_seen = defaultdict(int)  # All decks including those without cards
    
    # Aggregate data
    decks_with_cards = 0
    decks_without_cards = 0
    
    for i, deck in enumerate(all_decks):
        # NORMALIZE ARCHETYPE NAME to merge variants like "Ceruledge Ex" and "Ceruledge"
        archetype_raw = deck['archetype']
        archetype = normalize_archetype_name(archetype_raw)
        archetype_total_seen[archetype] += 1
        
        # Skip decks without card lists (from City League/Limitless Online)
        if not deck.get('cards'):
            decks_without_cards += 1
            continue
        
        decks_with_cards += 1
        archetype_deck_counts[archetype] += 1
        
        # Track which cards appear in this deck
        cards_in_deck = set()
        
        for card in deck['cards']:
            card_name = card['name']
            count = card['count']
            
            # Prefer set+number lookup to avoid truncated or incorrect names
            set_code = card.get('set_code', '')
            card_number = card.get('card_number', '')
            if set_code and card_number:
                looked_up_name = card_db.get_name_by_set_number(set_code, card_number)
                if looked_up_name:
                    if (not card_name or card_name.strip() == '' or
                        card_db.normalize_name(card_name) != card_db.normalize_name(looked_up_name)):
                        card_name = looked_up_name
                        card['name'] = card_name  # Update the card dict
            
            # If card name is still empty, skip
            if not card_name or card_name.strip() == '':
                continue
            
            archetype_cards[archetype][card_name]['total_count'] += count
            
            # Track max count across all decks
            if count > archetype_cards[archetype][card_name]['max_count']:
                archetype_cards[archetype][card_name]['max_count'] = count
            
            # Track set/number information for Pokemon cards
            if set_code and card_number:
                set_key = f"{set_code}_{card_number}"
                if set_key not in archetype_cards[archetype][card_name]['set_codes']:
                    archetype_cards[archetype][card_name]['set_codes'][set_key] = {'set_code': set_code, 'card_number': card_number, 'count': 0}
                archetype_cards[archetype][card_name]['set_codes'][set_key]['count'] += 1
            
            if card_name not in cards_in_deck:
                archetype_cards[archetype][card_name]['deck_count'] += 1
                cards_in_deck.add(card_name)
    
    print(f"\n📊 Data Summary:")
    print(f"  • Total decks collected: {len(all_decks)}")
    print(f"  • Decks WITH card lists: {decks_with_cards} (Tournament data)")
    print(f"  • Decks WITHOUT card lists: {decks_without_cards} (City League/Limitless archetype tracking)")
    print(f"  • Unique archetypes: {len(archetype_deck_counts)}")
    
    # Build final output
    result = []
    
    print(f"\n🔍 Looking up set/number info from card database...")
    card_count = 0
    successful_lookups = 0
    failed_lookups = 0
    
    for archetype, cards in archetype_cards.items():
        # Use only decks WITH cards for percentage calculation
        total_decks_with_cards = archetype_deck_counts[archetype]
        
        if total_decks_with_cards == 0:
            continue  # Skip archetypes with no card data
        
        for card_name, data in cards.items():
            # Calculate percentage based on decks that have card lists
            percentage = (data['deck_count'] / total_decks_with_cards * 100) if total_decks_with_cards > 0 else 0
            
            card_count += 1
            if card_count % 50 == 0:
                print(f"  Processed {card_count} unique cards... ({successful_lookups} found, {failed_lookups} not found)")
            
            # Determine which set/number to use
            card_info = None
            
            # If we have tracked set/numbers from the source (Pokemon case), use the most common one
            if data['set_codes']:
                # Find the most frequently occurring set/number combination
                most_common = max(data['set_codes'].items(), key=lambda x: x[1]['count'])
                set_code = most_common[1]['set_code']
                card_number = most_common[1]['card_number']
                
                # Check if this is a Trainer/Energy card
                is_trainer_energy = card_db.is_card_trainer_or_energy_by_name(card_name)
                
                # For Pokemon: Use the exact set/number from source
                # For Trainer/Energy: Use latest version without set/number
                if not is_trainer_energy:
                    # Pokemon card - keep the set/number
                    card_info = card_db.get_card_info_by_set_number(card_name, set_code, card_number)
                else:
                    # Trainer/Energy - use latest version (ignores source set/number)
                    card_info = card_db.get_card_info(card_name)
            else:
                # No source set/number info, do normal lookup
                card_info = card_db.get_card_info(card_name)
            
            if card_info:
                successful_lookups += 1
            else:
                failed_lookups += 1
            
            # Create identifier based on card type
            # Pokemon: "Set_Number" (e.g., "M3_055")
            # Trainer/Energy: Just the name (e.g., "Professor Sada")
            set_code_val = card_info['set_code'] if card_info else ''
            set_number_val = card_info['number'] if card_info else ''
            
            is_trainer_energy_final = card_db.is_card_trainer_or_energy_by_name(card_name)
            
            if is_trainer_energy_final:
                # Trainer/Energy: Just the name
                card_identifier = card_name
            else:
                # Pokemon: Use Set_Number format
                if set_code_val and set_number_val:
                    card_identifier = f"{set_code_val}_{set_number_val}"
                else:
                    # Fallback to just name if Set/Number not available
                    card_identifier = card_name
            
            result.append({
                'archetype': archetype,
                'card_name': card_name,
                'card_identifier': card_identifier,
                'total_count': data['total_count'],
                'max_count': data['max_count'],
                'deck_count': data['deck_count'],
                'total_decks_in_archetype': total_decks_with_cards,
                'percentage_in_archetype': round(percentage, 1),
                'set_code': card_info['set_code'] if card_info else '',
                'set_name': card_info['set_name'] if card_info else '',
                'set_number': card_info['number'] if card_info else '',
                'rarity': card_info['rarity'] if card_info else '',
                'image_url': card_info['image_url'] if card_info else ''
            })
    
    # Sort by archetype, then by percentage descending
    result.sort(key=lambda x: (x['archetype'], -x['percentage_in_archetype'], x['card_name']))
    
    print(f"\n✅ Final Results:")
    print(f"  • {len(result)} card entries across {len(archetype_cards)} archetypes")
    print(f"  • Lookup Summary: {successful_lookups} found ✓, {failed_lookups} not found ✗")
    if failed_lookups > 0:
        print(f"  ⚠️  {failed_lookups} cards missing set/number info (check all_cards_database.csv)")
    return result

def save_to_csv(data: List[Dict[str, Any]], output_file: str):
    """Save aggregated data to CSV."""
    if not data:
        print("No data to save.")
        return
    
    output_path = os.path.join(get_data_dir(), output_file)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"\nSaving data to: {output_path}")
    
    fieldnames = ['archetype', 'card_name', 'card_identifier', 'total_count', 'max_count', 'deck_count', 
                  'total_decks_in_archetype', 'percentage_in_archetype',
                  'set_code', 'set_name', 'set_number', 'rarity', 'image_url']
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for row in data:
                # Format percentage with comma for German Excel
                row_formatted = row.copy()
                row_formatted['percentage_in_archetype'] = str(row['percentage_in_archetype']).replace('.', ',')
                writer.writerow(row_formatted)
        
        print(f"Successfully saved {len(data)} entries to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 60)
    print("UNIFIED CARD SCRAPER")
    print("Combining City League, Limitless Online, and Tournament data")
    print("=" * 60)
    
    # Load settings
    settings = load_settings()
    
    # Initialize Card Database Lookup
    app_path = get_app_path()
    data_dir = get_data_dir()
    
    # Try multiple locations for the database
    possible_paths = [
        os.path.join(data_dir, 'all_cards_database.csv'),  # Primary: shared data folder
        os.path.join(app_path, 'all_cards_database.csv'),
        os.path.join(os.path.dirname(app_path), 'source', 'all_cards_database.csv'),
        os.path.join(os.path.dirname(app_path), 'all_cards_database.csv'),
        'C:\\Users\\haush\\OneDrive\\Desktop\\Hausi Scrapen\\source\\all_cards_database.csv'
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        print("\nERROR: all_cards_database.csv not found!")
        print("Please copy all_cards_database.csv to the same folder as the .exe")
        input("\nPress Enter to exit...")
        return
    
    print(f"Loading card database from: {csv_path}")
    card_db = CardDatabaseLookup(csv_path)
    
    if not card_db.cards:
        print("\nERROR: Failed to load card database!")
        input("\nPress Enter to exit...")
        return
    
    # Scrape from all enabled sources
    all_decks = []
    
    try:
        city_decks = scrape_city_league(settings, card_db)
        all_decks.extend(city_decks)
    except Exception as e:
        print(f"Error in City League scraping: {e}")
    
    try:
        limitless_decks = scrape_limitless_online(settings, card_db)
        all_decks.extend(limitless_decks)
    except Exception as e:
        print(f"Error in Limitless Online scraping: {e}")
    
    try:
        tournament_decks = scrape_tournaments(settings, card_db)
        all_decks.extend(tournament_decks)
    except Exception as e:
        print(f"Error in Tournament scraping: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total decks collected: {len(all_decks)}")
    print(f"{'='*60}")
    
    if not all_decks:
        print("\nNo decks found. Please check your settings and try again.")
        input("\nPress Enter to exit...")
        return
    
    # Aggregate and analyze
    aggregated_data = aggregate_card_data(all_decks, card_db)
    
    # Save to CSV
    save_to_csv(aggregated_data, settings['output_file'])
    
    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
