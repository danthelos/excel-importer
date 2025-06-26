import os

MEMORY_BANK_DIR = "memory-bank"
README_FILE = "README.md"

# Pliki do wczytania
FILES = {
    "projectbrief": "projectbrief.md",
    "activeContext": "activeContext.md",
    "progress": "progress.md",
    "systemPatterns": "systemPatterns.md",
    "techContext": "techContext.md",
    "productContext": "productContext.md",
    "memoryBankInstructions": "memory_bank_instructions.md"
}

def read_file_snippet(path, max_lines=12):
    """Wczytaj początkowe linie pliku markdown jako podsumowanie."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        # Pomijaj nagłówki i puste linie
        snippet = []
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                snippet.append(line.strip())
            if len(snippet) >= max_lines:
                break
        return " ".join(snippet)
    except Exception:
        return ""

def main():
    # Wczytaj podsumowania
    projectbrief = read_file_snippet(os.path.join(MEMORY_BANK_DIR, FILES["projectbrief"]))
    active_context = read_file_snippet(os.path.join(MEMORY_BANK_DIR, FILES["activeContext"]))
    progress = read_file_snippet(os.path.join(MEMORY_BANK_DIR, FILES["progress"]))

    # Generuj README.md
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("# Excel Data Importer\n\n")
        f.write("## Opis aplikacji\n\n")
        f.write(f"{projectbrief}\n\n")
        f.write("---\n\n")
        f.write("## Dla użytkownika\n\n")
        f.write("- **Cel**: Automatyczny import danych z plików Excel do bazy danych.\n")
        f.write("- **Jak używać**:\n")
        f.write("  1. Skonfiguruj plik `config.yaml` (ścieżki, dane logowania, itp.).\n")
        f.write("  2. Umieść pliki Excel w odpowiednim folderze lub bibliotece SharePoint.\n")
        f.write("  3. Uruchom aplikację:  \n     ```bash\n     python main.py\n     ```\n")
        f.write("  4. Przetworzone pliki trafią do folderu `imported` lub `broken` (w zależności od wyniku walidacji).\n\n")
        f.write("- **Wymagania**:\n")
        f.write("  - Python 3.8+\n  - PostgreSQL\n  - (opcjonalnie) SharePoint Server 2019\n\n")
        f.write("Więcej informacji: [Szczegółowy opis projektu](memory-bank/projectbrief.md)\n\n")
        f.write("---\n\n")
        f.write("## Dla developera\n\n")
        f.write("- **Architektura i fazy rozwoju**:  \n  Szczegóły znajdziesz w [projectbrief.md](memory-bank/projectbrief.md) oraz [progress.md](memory-bank/progress.md).\n")
        f.write("- **Aktualny stan projektu**:  \n  [Zobacz aktywny kontekst](memory-bank/activeContext.md)\n")
        f.write("- **Roadmapa i postępy**:  \n  [Zobacz postępy](memory-bank/progress.md)\n")
        f.write("- **Wzorce i decyzje systemowe**:  \n  [System Patterns](memory-bank/systemPatterns.md)\n")
        f.write("- **Kontekst techniczny**:  \n  [Tech Context](memory-bank/techContext.md)\n\n")
        f.write("---\n\n")
        f.write("## Dokumentacja Memory Bank\n\n")
        for key, filename in FILES.items():
            title = filename.replace(".md", "").replace("_", " ").title()
            f.write(f"- [{title}](memory-bank/{filename})\n")
        f.write("\n---\n\n")
        f.write("## Licencja\n\nMIT\n")

if __name__ == "__main__":
    main() 