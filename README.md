# Apple Photos Management Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-green.svg)](https://github.com/username/apple-photos-management)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/username/apple-photos-management/actions)

> **Profesionální nástroj pro export a organizaci fotografií z Apple Photos s pokročilými funkcemi optimalizace výkonu a modulární architekturou.**

## 🚀 **Rychlý start**

### Instalace
```bash
# 1. Klonování repository
git clone https://github.com/username/apple-photos-management.git
cd apple-photos-management

# 2. Automatická instalace
python scripts/setup.py

# 3. Aktivace virtuálního prostředí
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate     # Windows

# 4. Spuštění
python main.py --help
```

### Základní použití
```bash
# Dry-run (simulace bez kopírování)
python main.py dry /cesta/k/fotkam

# Skutečný export
python main.py run /cesta/k/fotkam /cesta/k/vystupu

# S pokročilými možnostmi
python main.py run /cesta/k/fotkam /cesta/k/vystupu \
  --duplicate-strategy preserve_duplicates \
  --workers 16 \
  --batch-size 200
```

## ✨ **Hlavní funkce**

### 🎯 **Univerzální podpora formátů**
- **Obrázky**: HEIC, JPG, JPEG, PNG, TIFF, TIF, RAW, CR2, NEF, ARW
- **Videa**: MOV, MP4, AVI, MKV, M4V
- **Metadata**: XMP, AAE (Apple Adjustment Export)
- **Automatická detekce** souvisejících souborů

### 📁 **Inteligentní organizace**
- **Chronologické třídění** podle data pořízení
- **YEAR-based struktura** (2023/, 2024/, ...)
- **Standardizované názvy** YYYYMMDD-HHMMSS-SSS.ext
- **Automatické řešení** konfliktů názvů

### 🔄 **Pokročilé duplikáty**
- **5 strategií řešení** duplicit
- **Hash-based detekce** s file type rozlišením
- **Inteligentní zachování** duplicit
- **Detailní statistiky** duplicit

### ⚡ **Optimalizace výkonu**
- **File Caching**: 50-70% snížení I/O operací
- **Batch Processing**: Optimalizované paralelní zpracování
- **Memory Optimization**: Streamové zpracování pro velké datové sady
- **Dynamic Worker Scaling**: Automatické škálování na základě systémových zdrojů
- **Real-time Monitoring**: Kontinuální sledování výkonu

### 🏗️ **Modulární architektura**
- **SOLID principy** - čisté oddělení odpovědností
- **Single Responsibility** - každá třída má jednu jasnou odpovědnost
- **Dependency Injection** - snadné testování a rozšiřování
- **Plugin Architecture** - připraveno pro budoucí rozšíření

### 🔒 **Bezpečnost**
- **Path Validation** - ochrana proti path traversal útokům
- **Input Sanitization** - sanitizace všech vstupních dat
- **Safe File Operations** - bezpečné file operace s proper error handling
- **User Directory Access** - bezpečný přístup k běžným uživatelským adresářům

## 📊 **Výsledky výkonu**

| Metrika | Hodnota | Popis |
|---------|---------|-------|
| **Rychlost zpracování** | 250-400 souborů/sekundu | Průměrná rychlost |
| **Snížení I/O** | 50-70% | Díky inteligentnímu cachování |
| **Snížení paměti** | 50% | Pro velké datové sady |
| **CPU využití** | Optimální | Automatické škálování workerů |
| **Škálovatelnost** | Lineární | S počtem dostupných jader |

## 🏗️ **Architektura**

### Modulární design
```
src/
├── core/                  # Jádro aplikace
│   ├── export_photos.py   # Hlavní orchestrátor
│   ├── duplicate_handler.py # Správa duplicit
│   ├── file_organizer.py  # Organizace souborů
│   ├── metadata_extractor.py # Extrakce metadat
│   ├── config.py          # Konfigurace
│   ├── models.py          # Datové modely
│   └── utils.py           # Utility funkce
├── logging/               # Logging systém
├── security/              # Bezpečnostní funkce
└── utils/                 # Performance monitoring
```

### Klíčové principy
- **Single Responsibility**: Každá třída má jednu jasnou odpovědnost
- **Open/Closed**: Snadné rozšiřování bez modifikace existujícího kódu
- **Dependency Inversion**: Závislosti na abstrakcích, ne na konkrétních implementacích
- **Interface Segregation**: Malé, specifické rozhraní místo velkých, obecných

## 📋 **Strategie duplicit**

| Strategie | Popis | Použití |
|-----------|-------|---------|
| `keep_first` | Zachová první výskyt | Výchozí, rychlé zpracování |
| `skip_duplicates` | Přeskočí všechny duplicity | Když chcete pouze unikátní fotky |
| `preserve_duplicates` | Zachová první + jeden duplikát | Pro archivaci s rezervou |
| `cleanup_duplicates` | Odstraní složku duplicit | Úklid po manuální kontrole |
| `!delete!` | Smaže duplicity z výstupu | Drastické řešení |

## 📁 **Výstupní struktura**

```
export_directory/
├── 20250925-143022/           # Timestamp exportu
│   ├── 2022/                  # Rok pořízení
│   │   ├── 20220310-091533-001.heic
│   │   ├── 20220310-091533-001.xmp
│   │   └── 20220310-091533-001.aae
│   ├── 2023/
│   │   ├── 20230615-143022-001.heic
│   │   └── 20230815-164511-001.mp4
│   └── 2024/
│       └── 20240101-120000-001.heic
│
├── duplicates_20250925-143022/ # Duplicity (pokud preserve_duplicates)
│   └── 2023/
│       └── 20230615-143022-002.heic
│
└── Log soubory
    ├── 20250925-143022_export.log
    ├── 20250925-143022_errors.log
    ├── 20250925-143022_metadata.json
    ├── 20250925-143022_summary.txt
    ├── 20250925-143022_performance_metrics.json
    └── 20250925-143022_performance_analysis.txt
```

## ⚙️ **Konfigurace**

### Environment proměnné
```bash
# .env soubor
EXPORT_WORKERS=8
EXPORT_BATCH_SIZE=100
EXPORT_CACHE_SIZE=10000
EXPORT_LOG_LEVEL=INFO
EXPORT_MEMORY_OPTIMIZATION=true
EXPORT_PERFORMANCE_MONITORING=true
```

### CLI parametry
```bash
python main.py [dry|run] <source_dir> [target_dir] [options]

Options:
  --duplicate-strategy STRATEGY  # Strategie duplicit
  --workers COUNT               # Počet workerů
  --batch-size SIZE            # Velikost batch
  --log-level LEVEL            # Úroveň logování
  --cache-size SIZE            # Velikost cache
  --memory-optimization        # Povolit memory optimization
  --performance-monitoring     # Povolit performance monitoring
  --help                       # Nápověda
```

## 🧪 **Testování**

### Spuštění testů
```bash
# Všechny testy
python -m pytest tests/ -v

# S pokrytím kódu
python -m pytest tests/ --cov=src --cov-report=html

# Konkrétní test
python -m pytest tests/test_core.py::test_photo_metadata_creation -v
```

### Testovací data
- **`examples/TestComprehensive/`** - Kompletní testovací dataset
- Zahrnuje různé formáty, metadata, duplicity a edge cases
- Používá se pro všechny automatické testy

## 🚀 **Deployment**

### Produkční nasazení
```bash
# 1. Vytvoření deployment balíčku
python scripts/deploy.py

# 2. Instalace na cílovém systému
python install.py

# 3. Konfigurace
cp env.example .env
# Upravit .env podle potřeby

# 4. Spuštění
python main.py run /source/path /target/path
```

### Docker deployment
```bash
# Build image
docker build -t apple-photos-management .

# Run container
docker run -v /source:/app/input -v /target:/app/output apple-photos-management

# Or use docker-compose
docker-compose up
```

## 📚 **Dokumentace**

### Hlavní dokumenty
- **[README.md](README.md)** - Tato dokumentace
- **[docs/project_structure.md](docs/project_structure.md)** - Detailní architektura
- **[docs/requirements.md](docs/requirements.md)** - Funkční požadavky
- **[docs/refactoring_summary.md](docs/refactoring_summary.md)** - Historie vylepšení
- **[docs/performance_analysis.md](docs/performance_analysis.md)** - Analýza výkonu
- **[docs/optimization_implementation.md](docs/optimization_implementation.md)** - Implementace optimalizací

### API dokumentace
- **[core/config.py](core/config.py)** - Konfigurace
- **[core/models.py](core/models.py)** - Datové modely
- **[core/utils.py](core/utils.py)** - Utility funkce

## 🤝 **Přispívání**

### Vývoj
1. Fork repository
2. Vytvoř feature branch (`git checkout -b feature/amazing-feature`)
3. Commit změny (`git commit -m 'Add amazing feature'`)
4. Push do branch (`git push origin feature/amazing-feature`)
5. Otevři Pull Request

### Reportování bugů
- Použij GitHub Issues
- Přilož log soubory a kroky k reprodukci
- Specifikuj verzi a operační systém

## 🆘 **Podpora**

### Troubleshooting
- **Chyby s HEIC**: Nainstaluj `pillow-heif`
- **Pomalé zpracování**: Zvyš počet workerů nebo batch size
- **Problémy s pamětí**: Sniž cache size nebo použij streaming mode

### Kontakt
- **Issues**: [GitHub Issues](https://github.com/username/apple-photos-management/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/apple-photos-management/discussions)

## 📄 **Licence**

Tento projekt je licencován pod MIT licencí - viz [LICENSE](LICENSE) soubor pro detaily.

## 🏆 **Uznání**

- **Pillow** - Python imaging library
- **loguru** - Modern logging library
- **tqdm** - Progress bars
- **psutil** - System monitoring
- **lxml** - XML processing

---

**Verze**: 2.0.0  
**Poslední aktualizace**: 2025-09-25  
**Python**: 3.8+  
**Status**: ✅ Produkční verze

---

<div align="center">

**Vytvořeno s ❤️ pro profesionální správu fotografií**

[⭐ Star na GitHub](https://github.com/username/apple-photos-management) • [🐛 Report Bug](https://github.com/username/apple-photos-management/issues) • [💡 Request Feature](https://github.com/username/apple-photos-management/issues)

</div>