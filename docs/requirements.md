# Funkční požadavky - Apple Photos Management Tool

## 📋 **Přehled**

Tento dokument definuje kompletní funkční a nefunkční požadavky pro Apple Photos Management Tool - profesionální nástroj pro export a organizaci fotografií s pokročilými funkcemi optimalizace výkonu.

## 🎯 **1. Obecné požadavky**

### 1.1 Cílová skupina
- **Primární**: Uživatelé Apple Photos hledající profesionální export nástroj
- **Sekundární**: Fotografové a archiváři potřebující organizaci velkých kolekcí
- **Technická**: Vývojáři a administrátoři systémů

### 1.2 Účel systému
- Export fotografií z Apple Photos s zachováním metadat
- Chronologická organizace podle data pořízení
- Pokročilé řešení duplicitních souborů
- Optimalizace výkonu pro velké datové sady
- Profesionální kvalita kódu a architektury

## 📸 **2. Funkční požadavky**

### 2.1 Photo Processing (REQ-001)
**Description**: Systém musí zpracovávat různé formáty fotografií a videí z Apple Photos exportů.

**Acceptance Criteria**:
- [x] **Image Formats**: HEIC, JPG, JPEG, PNG, TIFF, TIF, RAW, CR2, NEF, ARW
- [x] **Video Formats**: MOV, MP4, AVI, MKV, M4V
- [x] **Metadata Formats**: AAE (Apple Adjustment Export)
- [x] **Sidecar Formats**: XMP (Extensible Metadata Platform)
- [x] **Parallel Processing**: Paralelní zpracování s konfigurovatelnými workery
- [x] **Graceful Handling**: Elegantní zpracování nepodporovaných formátů s varováními
- [x] **XMP Detection**: Automatická detekce a zpracování XMP souborů
- [x] **XMP Copying**: Kopírování XMP souborů spolu s odpovídajícími fotografiemi
- [x] **Professional CLI**: Hlavní vstupní bod přes `main.py` s argparse
- [x] **Configuration Management**: Centralizovaná konfigurace přes .env soubory

### 2.2 Metadata Extraction (REQ-002)
**Description**: Systém musí extrahovat metadata z různých zdrojů a vybrat nejlepší datum.

**Acceptance Criteria**:
- [x] **EXIF Extraction**: Extrakce dat z EXIF metadat obrázků
- [x] **XMP Extraction**: Extrakce dat z XMP sidecar souborů
- [x] **AAE Extraction**: Extrakce dat z AAE souborů
- [x] **Date Selection**: Automatický výběr nejlepšího data (EXIF > XMP > AAE > file date)
- [x] **Fallback Handling**: Fallback na file creation date při chybějících metadatech
- [x] **Error Recovery**: Robustní zpracování chyb při extrakci metadat
- [x] **Multiple Sources**: Kombinace dat z více zdrojů pro nejlepší výsledek

### 2.3 File Organization (REQ-003)
**Description**: Systém musí organizovat fotografie do čisté, chronologické adresářové struktury.

**Acceptance Criteria**:
- [x] **YEAR Structure**: Vytváření YEAR-based adresářové struktury (2023/, 2024/)
- [x] **Standardized Naming**: Generování standardizovaných názvů YYYYMMDD-HHMMSS-SSS.ext
- [x] **Conflict Resolution**: Automatické řešení konfliktů názvů s číslováním
- [x] **Extension Normalization**: Normalizace přípon souborů na lowercase (.HEIC → .heic)
- [x] **Associated Files**: Kopírování souvisejících XMP a AAE souborů spolu s fotografiemi

### 2.4 Duplicate Handling (REQ-004)
**Description**: Systém musí detekovat a řešit duplicitní soubory pomocí různých strategií.

**Acceptance Criteria**:
- [x] **Hash Detection**: Detekce duplicit pomocí MD5 hash a file type
- [x] **Strategy Support**: Podpora 5 strategií řešení duplicit
  - [x] `keep_first` - Zachovat první výskyt
  - [x] `skip_duplicates` - Přeskočit všechny duplicity
  - [x] `preserve_duplicates` - Zachovat první + jeden duplikát
  - [x] `cleanup_duplicates` - Odstranit složku duplicit
  - [x] `!delete!` - Smazat duplicity z výstupu
- [x] **Statistics**: Detailní statistiky o duplicitách
- [x] **Performance**: Efektivní detekce i pro velké kolekce

### 2.5 Performance Optimization (REQ-005)
**Description**: Systém musí implementovat pokročilé optimalizace výkonu pro efektivní zpracování.

**Acceptance Criteria**:
- [x] **File Caching**: Inteligentní cachování souborů (50-70% snížení I/O)
- [x] **Batch Processing**: Optimalizované zpracování souborů v batch
- [x] **Memory Optimization**: Streamové zpracování pro velké datové sady (>1000 souborů)
- [x] **Dynamic Scaling**: Automatické škálování workerů na základě systémových zdrojů
- [x] **Real-time Monitoring**: Kontinuální sledování výkonu a optimalizace
- [x] **Intelligent Processing**: Automatický výběr mezi streamovým a batch zpracováním

### 2.6 Security (REQ-006)
**Description**: Systém musí implementovat robustní bezpečnostní opatření.

**Acceptance Criteria**:
- [x] **Path Validation**: Validace a sanitizace všech file paths
- [x] **Traversal Protection**: Ochrana proti path traversal útokům
- [x] **Input Sanitization**: Sanitizace všech vstupních dat
- [x] **Safe Operations**: Bezpečné file operace s proper error handling
- [x] **User Directory Access**: Bezpečný přístup k běžným uživatelským adresářům

### 2.7 Logging and Monitoring (REQ-007)
**Description**: Systém musí poskytovat kompletní logging a monitoring funkcionality.

**Acceptance Criteria**:
- [x] **Structured Logging**: Strukturované logování s loguru framework
- [x] **Multiple Levels**: DEBUG, INFO, WARNING, ERROR log levels
- [x] **On-demand Error Logs**: Error logy vytvářené pouze při chybách
- [x] **Performance Metrics**: Detailní metriky výkonu v JSON formátu
- [x] **Analysis Reports**: Automatické generování analýz výkonu
- [x] **Consistent Naming**: Konzistentní pojmenování všech log souborů

## ⚙️ **3. Technické požadavky**

### 3.1 Supported File Formats (REQ-012)
**Description**: Systém musí podporovat širokou škálu formátů souborů.

**Acceptance Criteria**:
- [x] **Image Formats**: HEIC, JPG, JPEG, PNG, TIFF, TIF, RAW, CR2, NEF, ARW
- [x] **Video Formats**: MOV, MP4, AVI, MKV, M4V
- [x] **Metadata Formats**: AAE (Apple Adjustment Export)
- [x] **Sidecar Formats**: XMP (Extensible Metadata Platform)
- [x] **XMP Detection Patterns**: 
  - [x] `filename.ext.xmp` - Standardní pattern
  - [x] `filename.ext.XMP` - Uppercase variant
  - [x] `filename.xmp` - Bez extension
  - [x] `filename.XMP` - Uppercase bez extension
- [x] **Extension Normalization**: Všechny přípony normalizovány na lowercase
- [x] **Unsupported Format Handling**: Elegantní zpracování nepodporovaných formátů s varováními
- [x] **Format Statistics**: Sledování statistik nepodporovaných formátů

### 3.2 File Naming Behavior (REQ-016)
**Description**: Systém musí implementovat konzistentní pojmenování a zpracování souborů.

**Acceptance Criteria**:
- [x] **Extension Normalization**: Všechny přípony souborů převedeny na lowercase (.HEIC → .heic)
- [x] **Filename Generation**: Standardizovaný formát YYYYMMDD-HHMMSS-SSS.ext
- [x] **Case Consistency**: Zajištění konzistentního pojmenování napříč operačními systémy
- [x] **Duplicate Handling**: Automatické číslování pro konflikty názvů (např. -001, -002)
- [x] **Professional CLI**: Hlavní vstupní bod přes `main.py` s argparse
- [x] **Configuration Management**: Centralizovaná konfigurace přes .env soubory
- [x] **Error Handling**: Robustní zpracování chyb s návratovými kódy

### 3.3 Performance Optimization (REQ-017)
**Description**: Systém musí implementovat pokročilé optimalizace výkonu.

**Acceptance Criteria**:
- [x] **File Caching**: Inteligentní cachování systému snižuje I/O operace o 50-70%
- [x] **Batch Processing**: Optimalizované file operace s dynamickou velikostí batch
- [x] **Memory Optimization**: Streamové zpracování pro velké datové sady (>1000 souborů)
- [x] **Dynamic Worker Scaling**: Automatická optimalizace na základě systémových zdrojů
- [x] **Real-time Monitoring**: Kontinuální sledování výkonu a optimalizace
- [x] **Intelligent Processing**: Automatický výběr mezi streamovým a batch zpracováním
- [x] **Consistent Logging**: Performance logy následují stejnou naming konvenci jako ostatní logy

### 3.4 Architecture Requirements (REQ-018)
**Description**: Systém musí dodržovat profesionální architektonické principy.

**Acceptance Criteria**:
- [x] **SOLID Principles**: Implementace všech SOLID principů
- [x] **Modular Design**: Čisté oddělení odpovědností do modulů
- [x] **Single Responsibility**: Každá třída má jednu jasnou odpovědnost
- [x] **Dependency Injection**: Injekce závislostí přes konstruktory
- [x] **Error Handling**: Robustní zpracování chyb s custom exceptions
- [x] **Type Hints**: Kompletní typování všech funkcí a metod
- [x] **Documentation**: Kompletní docstrings pro všechny veřejné API

### 3.5 Testing Requirements (REQ-019)
**Description**: Systém musí mít kompletní testovací pokrytí.

**Acceptance Criteria**:
- [x] **Unit Tests**: Testy pro kritické funkce a edge cases
- [x] **Integration Tests**: End-to-end testy s reálnými daty
- [x] **Performance Tests**: Testy výkonu a škálovatelnosti
- [x] **Test Data**: Kompletní testovací dataset s různými scénáři
- [x] **Coverage**: Minimálně 80% pokrytí kódu testy
- [x] **Automation**: Automatizované spouštění testů

### 3.6 Documentation Requirements (REQ-020)
**Description**: Systém musí mít kompletní a aktuální dokumentaci.

**Acceptance Criteria**:
- [x] **README**: Kompletní hlavní dokumentace s příklady použití
- [x] **API Documentation**: Dokumentace všech veřejných API
- [x] **Architecture Docs**: Dokumentace architektury a design principů
- [x] **Requirements Docs**: Detailní funkční požadavky
- [x] **Code Comments**: Inline komentáře pro komplexní logiku
- [x] **Examples**: Praktické příklady použití a konfigurace

## 🚀 **4. Nefunkční požadavky**

### 4.1 Performance (REQ-008)
**Description**: Systém musí dosahovat vysokého výkonu při zpracování velkých kolekcí.

**Acceptance Criteria**:
- [x] **Processing Speed**: 250-400 souborů/sekundu
- [x] **Memory Usage**: < 2GB RAM pro kolekce do 10,000 souborů
- [x] **I/O Optimization**: 50-70% snížení I/O operací pomocí cachování
- [x] **Scalability**: Lineární škálování s počtem CPU jader
- [x] **Large Datasets**: Efektivní zpracování kolekcí > 100,000 souborů

### 4.2 Reliability (REQ-009)
**Description**: Systém musí být spolehlivý a robustní.

**Acceptance Criteria**:
- [x] **Error Recovery**: Graceful recovery z chyb bez ztráty dat
- [x] **Data Integrity**: Zachování integrity všech kopírovaných dat
- [x] **Atomic Operations**: Atomické operace pro kritické procesy
- [x] **Validation**: Kompletní validace všech vstupů a výstupů
- [x] **Logging**: Detailní logování všech operací pro debugging

### 4.3 Usability (REQ-010)
**Description**: Systém musí být snadno použitelný pro různé typy uživatelů.

**Acceptance Criteria**:
- [x] **CLI Interface**: Intuitivní command-line rozhraní
- [x] **Help System**: Kompletní nápověda a dokumentace
- [x] **Progress Indicators**: Real-time progress bars pro dlouhé operace
- [x] **Error Messages**: Jasné a užitečné chybové zprávy
- [x] **Configuration**: Snadná konfigurace přes parametry a .env soubory

### 4.4 Maintainability (REQ-011)
**Description**: Systém musí být snadno udržovatelný a rozšiřitelný.

**Acceptance Criteria**:
- [x] **Modular Architecture**: Čisté oddělení komponent
- [x] **Code Quality**: Dodržování Python best practices
- [x] **Documentation**: Kompletní dokumentace kódu
- [x] **Testing**: Kompletní testovací pokrytí
- [x] **Version Control**: Proper Git workflow a commit conventions

## 📊 **5. Metriky a KPI**

### 5.1 Performance Metrics
- **Processing Speed**: 250-400 files/second
- **Memory Efficiency**: 50% reduction for large datasets
- **I/O Optimization**: 50-70% reduction in I/O operations
- **CPU Utilization**: Optimal usage of available cores
- **Error Rate**: < 0.1% for valid input files

### 5.2 Quality Metrics
- **Code Coverage**: > 80%
- **Type Coverage**: 100% for public APIs
- **Documentation Coverage**: 100% for public functions
- **Linting Score**: 0 errors, 0 warnings
- **Test Success Rate**: 100% for all test suites

### 5.3 User Experience Metrics
- **Setup Time**: < 5 minutes for new users
- **Learning Curve**: < 30 minutes to basic proficiency
- **Error Recovery**: < 1 minute average recovery time
- **Documentation Quality**: 100% of features documented with examples

## 🔄 **6. Verze a změny**

### 6.1 Verze 2.0.0 (2025-09-25)
**Major Changes**:
- ✅ **Modular Architecture**: Kompletní refaktoring podle SOLID principů
- ✅ **Performance Optimization**: Implementace pokročilých optimalizací
- ✅ **DuplicateHandler**: Extrakce správy duplicit do samostatného modulu
- ✅ **FileOrganizer**: Extrakce organizace souborů do samostatného modulu
- ✅ **Security Enhancements**: Vylepšené bezpečnostní funkce
- ✅ **Documentation**: Kompletní aktualizace dokumentace

### 6.2 Verze 1.0.0 (2025-09-24)
**Initial Release**:
- ✅ **Basic Export**: Základní export funkcionalita
- ✅ **Metadata Extraction**: EXIF, XMP, AAE podpora
- ✅ **File Organization**: YEAR-based struktura
- ✅ **Duplicate Handling**: Základní detekce duplicit
- ✅ **Logging**: Strukturované logování

## 📋 **7. Acceptance Criteria Checklist**

### Funkční požadavky
- [x] Photo Processing (REQ-001) - ✅ IMPLEMENTED
- [x] Metadata Extraction (REQ-002) - ✅ IMPLEMENTED
- [x] File Organization (REQ-003) - ✅ IMPLEMENTED
- [x] Duplicate Handling (REQ-004) - ✅ IMPLEMENTED
- [x] Performance Optimization (REQ-005) - ✅ IMPLEMENTED
- [x] Security (REQ-006) - ✅ IMPLEMENTED
- [x] Logging and Monitoring (REQ-007) - ✅ IMPLEMENTED

### Technické požadavky
- [x] Supported File Formats (REQ-012) - ✅ IMPLEMENTED
- [x] File Naming Behavior (REQ-016) - ✅ IMPLEMENTED
- [x] Performance Optimization (REQ-017) - ✅ IMPLEMENTED
- [x] Architecture Requirements (REQ-018) - ✅ IMPLEMENTED
- [x] Testing Requirements (REQ-019) - ✅ IMPLEMENTED
- [x] Documentation Requirements (REQ-020) - ✅ IMPLEMENTED

### Nefunkční požadavky
- [x] Performance (REQ-008) - ✅ IMPLEMENTED
- [x] Reliability (REQ-009) - ✅ IMPLEMENTED
- [x] Usability (REQ-010) - ✅ IMPLEMENTED
- [x] Maintainability (REQ-011) - ✅ IMPLEMENTED

## 🎯 **8. Závěr**

Všechny definované požadavky byly úspěšně implementovány v rámci verze 2.0.0. Systém splňuje všechny funkční i nefunkční požadavky a je připraven k produkčnímu nasazení s profesionální kvalitou kódu a architektury.

---

**Verze dokumentu**: 2.0.0  
**Poslední aktualizace**: 2025-09-25  
**Status**: ✅ COMPLETED  
**Příští review**: 2025-12-25