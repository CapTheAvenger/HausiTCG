# 🎴 Unified Scraper TCG

Komplettes Pokemon TCG Scraping & Deck Analysis System mit HTML Comparison Reports

## 📁 Ordnerstruktur

```
Unified Scraper TCG/
├── dist/                         # 🎯 Fertige Executables (EXE + Settings)
│   ├── city_league_archetype_scraper/
│   │   ├── city_league_archetype_scraper.exe
│   │   └── city_league_archetype_settings.json
│   ├── limitless_online_scraper/
│   │   ├── limitless_online_scraper.exe
│   │   └── limitless_online_settings.json
│   └── unified_card_scraper/
│       ├── unified_card_scraper.exe
│       └── unified_card_settings.json
├── data/                         # 📊 Generierte Daten (CSV + HTML)
│   ├── city_league_archetypes.csv
│   ├── city_league_archetypes_comparison.csv
│   ├── city_league_archetypes_comparison.html ✨ NEU!
│   ├── city_league_archetypes_deck_stats.csv
│   ├── limitless_online_decks.csv
│   ├── limitless_online_decks_comparison.csv
│   ├── limitless_online_decks_comparison.html ✨
│   ├── limitless_online_decks_matchups.csv
│   ├── unified_card_data.csv
│   ├── all_cards_database.csv
│   └── archive/                  # Alte Daten (nach RESET_STATS.bat)
├── web/                          # 🌐 Web Interface
│   └── deck_viewer.html
├── scripts/                      # 🐍 Python Source Code
│   ├── city_league_archetype_scraper.py
│   ├── limitless_online_scraper.py
│   ├── unified_card_scraper.py
│   └── card_type_lookup.py
├── RUN_ALL_SCRAPERS.bat          # 🚀 Startet alle Scraper
├── RESET_STATS.bat               # 🔄 Reset für neues Meta
└── OPEN_VIEWER.bat               # 🌐 Öffnet Deck Viewer

```

## 🚀 Schnellstart

### 1️⃣ Alle Scraper ausführen
Doppelklick auf: **`RUN_ALL_SCRAPERS.bat`**
- Führt alle 3 Scraper nacheinander aus:
  1. City League Archetype Scraper
  2. Limitless Online Scraper
  3. Unified Card Scraper
- Erstellt CSV + HTML Comparison Reports
- Dauert ca. 10-20 Minuten

### 2️⃣ HTML Reports ansehen
Die HTML-Dateien im `data/` Ordner direkt im Browser öffnen:
- **`city_league_archetypes_comparison.html`** - City League Trends
- **`limitless_online_decks_comparison.html`** - Limitless Meta Analysis

### 3️⃣ Deck Viewer öffnen
Doppelklick auf: **`OPEN_VIEWER.bat`**
- Öffnet den interaktiven Deck Viewer

### 4️⃣ Meta-Wechsel Reset
Doppelklick auf: **`RESET_STATS.bat`**
- Archiviert alte Daten mit Timestamp
- Bereitet sauberen Start für neues Meta vor
- all_cards_database.csv bleibt erhalten

## 📊 Features

### City League Archetype Scraper
- ✅ Scraped Japanese City League Turniere
- ✅ Archetype Tracking & Statistics
- ✅ HTML Comparison Report mit:
  - Neue/Verschwundene Archetypes
  - Popularity Increases/Decreases
  - Performance Improvers/Decliners
  - Average Placement Trends

### Limitless Online Scraper
- ✅ Top Deck Rankings von Limitless Online
- ✅ Win Rate & Matchup Analysis
- ✅ HTML Comparison Report mit:
  - Top 10 Movements (Enter/Leave)
  - Rank Climbers/Fallers
  - Detailed Matchup Tables (Best/Worst)
  - Meta Trend Visualization

### Unified Card Scraper
- ✅ Kombiniert alle Quellen
- ✅ Card Usage Statistics
- ✅ Set/Number Information
- ✅ Archetype Percentage Breakdown

## ⚙️ Settings Anpassen

Alle Settings-Dateien befinden sich direkt bei den EXEs in `dist/`:

**City League**: `dist/city_league_archetype_scraper/city_league_archetype_settings.json`
```json
{
    "start_date": "24.01.2026",
    "end_date": "auto",
    "delay_between_requests": 1.5,
    "output_file": "city_league_archetypes.csv",
    "region": "jp"
}
```

**Limitless Online**: `dist/limitless_online_scraper/limitless_online_settings.json`
```json
{
    "game": "POKEMON",
    "format": "STANDARD",
    "rotation": "2025",
    "set": "PFL",
    "top_decks_for_matchup": 100,
    "delay_between_requests": 1.5
}
```

## 📋 Output-Dateien

### CSV-Dateien
- Delimiter: `;` (Semikolon)
- Encoding: UTF-8-BOM
- Dezimaltrennzeichen: `,` (Komma für Excel)

### HTML-Dateien  
- Responsive Design
- Sortierbare Tabellen
- Color-Coded Trends (Grün/Rot/Grau)
- Embedded CSS (keine externen Dependencies)

## 🔧 Entwicklung

Python Sourcecode in `scripts/`:
- Alle Scraper verwenden nur Python Standard Library
- Keine externen Dependencies erforderlich
- Können direkt mit Python ausgeführt werden

## 📝 Workflow für Meta-Update

1. **`RESET_STATS.bat`** ausführen → Archiviert alte Daten
2. **`RUN_ALL_SCRAPERS.bat`** ausführen → Sammelt neue Daten
3. Nach 1-2 Wochen erneut **`RUN_ALL_SCRAPERS.bat`** → Erstellt Comparison
4. **HTML Reports** öffnen → Analysiere Meta-Trends

## 🎯 Wichtige Hinweise

- ⚠️ **First Run**: Beim ersten Lauf gibt es keine Comparison (keine alten Daten)
- 💡 **Comparison Reports**: Werden erst beim 2. Run erstellt (alter vs neuer Datensatz)
- 📦 **all_cards_database.csv**: Wird von RESET_STATS NICHT gelöscht
- ⏱️ **Rate Limiting**: Delays zwischen Requests sind konfigurierbar
- ✅ Win-Rate Statistiken
- ✅ Top & Worst Matchups
- ✅ Deck-Varianten vergleichen
- ✅ Auto-Build Funktion
- ✅ In Zwischenablage kopieren
- ✅ Mobile-optimiert

### Scraper
1. **Unified Card Scraper**: Erstellt komplette Kartendatenbank mit Types
2. **Limitless Online Scraper**: Top Decks, Win-Rates, alle Matchup-Daten
3. **City League Archetype Scraper**: Japan Turnier-Daten und Trends

## ⚙️ Konfiguration

Alle Settings in `settings/` anpassen:
- Format, Rotation, Set-Code
- Anzahl Top-Decks für Matchup-Analyse
- Delay zwischen Requests

## 🔧 Manuelle Ausführung

```bash
# Einzelne Scraper ausführen (im scripts/ Ordner)
cd scripts
python unified_card_scraper.py
python limitless_online_scraper.py
python city_league_archetype_scraper.py

# Web-Server manuell starten (im web/ Ordner)
cd web
python -m http.server 8000
```

## 📝 Hinweise

- Python 3.x erforderlich  
- Keine zusätzlichen Dependencies nötig (nur Standard Library)
- Alle Daten werden automatisch in `data/` gespeichert
- Bei Problemen: Hard-Refresh im Browser (Ctrl+Shift+R)

## 🎯 Workflow

1. **Einmalig**: Daten mit `RUN_SCRAPERS.bat` generieren
2. **Täglich**: Viewer mit `START_VIEWER.bat` öffnen
3. **Bei Updates**: Scraper erneut ausführen
