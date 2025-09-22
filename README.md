# Apple Photos Export Tool

Nástroj pro export a organizaci fotografií z Apple Photos knihovny. Automaticky čte fotky a XMP soubory, extrahuje data vytvoření z EXIF a XMP metadat, vybere dřívější datum a organizuje fotky do struktury YEAR/MM/DD.

## Funkce

- ✅ **Export z Apple Photos** - Přečte exportované fotky a XMP soubory
- ✅ **Inteligentní datum** - Vybere dřívější datum mezi EXIF a XMP
- ✅ **Organizace** - Vytvoří strukturu YEAR/MM/DD
- ✅ **Přejmenování** - Formát YYYYMMDD-HHMMSS-SSS.ext
- ✅ **Duplicity** - Automatické řešení duplicitních názvů
- ✅ **Dry-run** - Testovací režim bez skutečného kopírování
- ✅ **Logování** - Detailní logy a statistiky
- ✅ **Různé formáty** - HEIC, JPG, PNG, MOV, MP4 a další
- ✅ **Bezpečnost** - Vytvoří nový adresář pro každý export

## Instalace

### Požadavky
- macOS (testováno na macOS 10.15+)
- Python 3.8+
- Apple Photos s exportovanými soubory

### Instalace závislostí
```bash
pip3 install -r requirements.txt
```

## Použití

### Základní použití
```bash
# Test v aktuálním adresáři
./export_photos.sh

# Test se specifikovanými adresáři
./export_photos.sh /path/to/photos /path/to/output

# Spuštění na ostro
./export_photos.sh /path/to/photos /path/to/output run
```

### Parametry
- `source_dir` - Adresář s exportovanými fotkami a XMP soubory (volitelné, výchozí: aktuální adresář)
- `target_dir` - Adresář pro organizované fotky (volitelné, výchozí: aktuální adresář)
- `run_mode` - "run" pro spuštění, cokoliv jiného pro dry-run test

## Jak to funguje

### 1. Export z Apple Photos
1. Otevřete Apple Photos
2. Vyberte fotky nebo celou knihovnu
3. File → Export → Export Originals
4. Uložte do adresáře (zachová XMP soubory)

### 2. Spuštění nástroje
```bash
# Nejdříve test
./export_photos.sh /path/to/exported/photos /path/to/organized/photos

# Pokud je vše v pořádku, spusťte na ostro
./export_photos.sh /path/to/exported/photos /path/to/organized/photos run
```

### 3. Výsledek
```
organized_photos/
├── export_20250115-143022/    # Timestamp exportu
│   ├── 2023/
│   │   ├── 01/
│   │   │   ├── 15/
│   │   │   │   ├── 20230115-143022-001.HEIC
│   │   │   │   └── 20230115-143022-002.JPG
│   │   └── 06/
│   │       └── 20/
│   │           └── 20230620-091533-001.PNG
│   ├── 2024/
│   │   └── 03/
│   │       └── 10/
│   │           └── 20240310-164511-001.MOV
│   ├── export_log.txt
│   ├── export_summary.txt
│   └── export_metadata.json
```

## Podporované formáty

### Obrázky
- HEIC (iPhone fotky)
- JPG/JPEG
- PNG
- TIFF/TIF
- RAW (CR2, NEF, ARW)

### Videa
- MOV
- MP4
- AVI
- MKV
- M4V

## Logika výběru data

Nástroj používá inteligentní logiku pro výběr nejlepšího data vytvoření:

1. **EXIF datum** - Skutečné datum pořízení z kamery
2. **XMP datum** - Datum z Apple Photos metadat
3. **Dřívější datum** - Vybere dřívější z EXIF a XMP
4. **Fallback** - Pokud chybí oba, použije datum souboru

### Proč dřívější datum?
- EXIF obsahuje skutečné datum pořízení
- XMP může obsahovat datum importu (pozdější)
- Dřívější datum je vždy správné datum pořízení

## Řešení duplicit

Při stejných časech vytvoření:
- `20231215-143022-001.HEIC`
- `20231215-143022-002.JPG`
- `20231215-143022-003.PNG`

## Testování

### Spuštění testů
```bash
# Všechny testy
python3 -m pytest test_export_photos.py -v

# Konkrétní test
python3 -m pytest test_export_photos.py::TestPhotoExporter::test_basic_functionality -v

# S coverage
python3 -m pytest test_export_photos.py --cov=export_photos --cov-report=html
```

### Testovací data
Nástroj byl testován na:
- `/Users/Ilja_Iljuchin/Developer/apple-photos-management/Test1` - Málo dat
- `/Users/Ilja_Iljuchin/Developer/apple-photos-management/Test2` - Více dat
- `/Users/Ilja_Iljuchin/Developer/apple-photos-management/TestFull2025` - Plná galerie

## Logování

### Úrovně logů
- **INFO** - Základní informace o procesu
- **WARNING** - Varování (nepodporované formáty, duplicity)
- **ERROR** - Chyby při zpracování
- **DEBUG** - Detailní informace pro debugging

### Log soubory
- `export_log_YYYYMMDD-HHMMSS.txt` - Detailní log
- `export_summary.txt` - Shrnutí exportu
- `export_metadata.json` - Metadata v JSON formátu

## Bezpečnost

### Ochrana dat
- **Žádné přepsání** - Vždy vytvoří nový adresář
- **Timestamp exportu** - Každý export má unikátní název
- **Dry-run režim** - Testování bez rizika
- **Backup logů** - Všechny operace jsou zaznamenány

### Historie exportů
```
target_directory/
├── export_20250115-143022/    # První export
├── export_20250115-154510/    # Druhý export
├── export_20250115-162033/    # Třetí export
└── export_history.txt         # Historie všech exportů
```

## Troubleshooting

### Časté problémy

#### 1. Chybějící závislosti
```bash
pip3 install -r requirements.txt --user
```

#### 2. Oprávnění k zápisu
```bash
chmod +x export_photos.sh
chmod +x export_photos.py
```

#### 3. Chybějící XMP soubory
- Ujistěte se, že exportujete s "Export Originals"
- XMP soubory jsou vytvářeny automaticky

#### 4. Nesprávné datum
- Zkontrolujte EXIF data v originálních souborech
- XMP může obsahovat datum importu místo pořízení

### Debug režim
```bash
# Spuštění s debug výstupem
python3 export_photos.py /path/to/source /path/to/target true
```

## Vývoj

### Struktura projektu
```
apple-photos-management/
├── export_photos.sh          # Shell wrapper
├── export_photos.py          # Hlavní Python skript
├── test_export_photos.py     # Test suite
├── requirements.txt          # Python závislosti
├── README.md                 # Dokumentace
├── Test1/                    # Testovací data (málo)
├── Test2/                    # Testovací data (více)
└── TestFull2025/             # Testovací data (plná galerie)
```

### Přidání nových formátů
Upravte `SUPPORTED_FORMATS` v `PhotoExporter` třídě:
```python
SUPPORTED_FORMATS = {'.heic', '.jpg', '.jpeg', '.png', '.mov', '.mp4', '.new_format'}
```

### Přidání nových metadat
Rozšiřte `PhotoMetadata` dataclass a odpovídající parsery.

## Licence

MIT License - viz LICENSE soubor pro detaily.

## Podpora

Pro problémy a dotazy vytvořte issue v GitHub repository.

---

**Poznámka**: Tento nástroj je navržen pro použití s exportovanými soubory z Apple Photos. Pro přímý přístup k Photos knihovně by bylo potřeba použít Photos framework API.
