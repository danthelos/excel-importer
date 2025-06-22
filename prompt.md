## 🧩 Opis zadania – Import danych Excel z SharePoint do PostgreSQL

### 🎯 Cel
Stwórz aplikację w Pythonie, która automatycznie importuje dane z plików Excel umieszczanych w bibliotece SharePoint i zapisuje je w tabeli `blacklist.entity` w bazie PostgreSQL. Mechanizm będzie zintegrowany z DAG Airflow i umożliwia walidację danych, logowanie zdarzeń oraz obsługę błędów.

---

### 🛠️ Techniczne wymagania – Faza 1

- Przechowuj konfigurację w pliku `config.yaml`, zawierającym m.in.:
  - `sharepoint_user_login`
  - `sharepoint_user_password`
  - `sharepoint_library_url`
  - `db_user_login`
  - `db_user_password`
  - `db_host`
  - `db_port`
  - `db_name`

- Struktura aplikacji:
  - Główny plik ładuje zmienne z YAML i korzysta z funkcji pomocniczych z `utils.py`.
  - Wszystkie funkcje (logika importu, walidacja, zapis) powinny znaleźć się w `utils.py`.

- Działanie aplikacji:
  - Monitoruj bibliotekę SharePoint i wykrywaj nowe pliki Excel.
  - Pobierz login AD użytkownika, który zapisał plik (właściwość pliku).
  - Zaczytaj dane z dwóch sekcji:
    - **Kolumny stałe** (od `Typ identyfikatora` do `Data obowiązywania do`)
    - **Dane opisowe** – wszystkie pozostałe kolumny zostają zapisane jako jedna kolumna `dane_opisowe` typu `jsonb`
  - Przed zapisaniem danych:
    - Uzupełnij pustą wartość pola `Produkt` wartością `"all"`
    - Sprawdź, czy wszystkie kolumny stałe istnieją w pliku
    - Zweryfikuj dane opisowe względem słownika:
      - Jeśli kolumna nie istnieje w słowniku – pomiń ją
      - Jeśli istnieje – sprawdź zgodność typu danych
  - W przypadku błędów:
    - Wyślij e-mail do użytkownika (`login`)
    - Przenieś plik do folderu `broken` na SharePoint
  - Jeśli rekord (kombinacja `id_type`, `id_value`, `product`) już istnieje:
    - Pobierz `dane_opisowe` ze starego rekordu
    - Utwórz nowy rekord z nowym `version` (timestamp)
    - Połącz dane opisowe ze starego i nowego rekordu
    - Stary rekord pozostaje bez zmian
  - Jeśli wszystko się powiedzie:
    - Zapisz dane jako nowy rekord
    - Przenieś plik do folderu `imported`

- Kolumna `version` ma być wypełniana bieżącym timestampem.
- Zdarzenia procesu powinny być logowane w formacie JSON umożliwiającym eksport do ElasticSearch. W logu m.in.: `timestamp`, `level`, `action`, `message`.

---

### 🔁 Techniczne wymagania – Faza 2

- Przekształć mechanizm w **DAG Airflow**.
- Walidacja `dane_opisowe` ma korzystać z REST API zamiast lokalnego pliku. Wymaga to:
  - Dodania zmiennych `schema_api_user`, `schema_api_password`, `schema_api_url` do pliku YAML
  - Modyfikacji funkcji walidującej, aby pobierała schemat przez API

---

### 📌 Mapowanie kolumn z pliku Excel do struktury bazy danych

Wymagany jest plik `kolumny_mapowanie.json`, który odwzorowuje nagłówki z Excela na kolumny bazy danych:

```json
{
  "Typ identyfikatora": "id_type",
  "Identyfikator": "id_value",
  "Produkt": "product",
  "Aktywny": "is_active",
  "Data obowiązywania od": "data_od",
  "Data obowiązywania do": "data_do"
}
```
Pozostałe kolumny nieujęte w mapowaniu zostaną zapisane jako jsonb pod kluczem dane_opisowe.

### Schematy pomocnicze

#### kolumny_stale.json:  

```json
{
  "id_type": "VARCHAR(255)",
  "id_value": "VARCHAR(255)",
  "product": "VARCHAR(255)",
  "login": "VARCHAR(255)",
  "data_od": "DATETIME",
  "data_do": "DATETIME",
  "dane_opisowe": "jsonb",
  "version": "TIMESTAMP"
}
```

#### dane_opisowe.json:  

```json
{
  "taxi": "boolean",
  "czy włoski": "boolean",
  "prius": "boolean",
  "Prawdopodobieństwo zalania": "float",
  "Notatka": "string",
  "Ostatnia wizyta": "date"
}
```
### Przykładowe schematy pomocnicze

#### Przykładowa tabela z danymi do importu:

| Typ identyfikatora | Identyfikator       | Produkt | Aktywny | Data obowiązywania od | Data obowiązywania do | taxi | czy włoski | prius | Prawdopodobieństwo zalania | Notatka | Ostatnia wizyta |
|--------------------|---------------------|---------|---------|------------------------|------------------------|------|------------|--------|-----------------------------|---------|------------------|
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | nie  | nie        | nie    |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076408   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | nie  | tak        | tak    |                             |         |                  |
| NR_DZIAŁKI         | 146518_8.0103.31/2  | ROLNE   | nie     | 2024-07-01             | 2025-07-01             |  	|		|     |       123                      |         |                  |
| NR_DZIAŁKI         | 146503_8.0109.61    | DOM     | tak     | 2024-07-01             | 2025-07-01             |   |         |    |                             |         |                  |
| NR_REJ             | WA12345             | AUTO    | tak     | 2024-07-01             | 2025-07-01             | tak  | tak        | tak    |                             |         |                  |
| PESEL              | 78030714992         | AUTO    | tak     | 2024-07-01             | 2025-07-01             |  |         |     |                             |     | 2025-07-01       |
| PESEL              | 6231287548          | DOM     | tak     | 2024-07-01             | 2025-07-01             |   |         |     |                             |      |                  |
| PESEL              | 69071351178         | ROLNE   | tak     | 2024-07-01             | 2025-07-01             |   |        |     |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | tak  | tak        | tak    |                             |         |                  |
| PESEL              | 52030478900         |         | tak     | 2024-08-01             | 2025-08-01             |   |         |     |                        | brak     | 2025-04-15       |

#### Przekształcone rekordy
VIN (Product = AUTO)

```json
{
  "id_type": "VIN",
  "id_value": "WWWZZZ3BZ4E076409",
  "product": "AUTO",
  "is_active": "tak",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "taxi": "nie",
    "czy włoski": "tak",
    "prius": "tak"
  }
}
```

NR_DZIAŁKI (Produkt = ROLNE)

```json
{
  "id_type": "NR_DZIAŁKI",
  "id_value": "146518_8.0103.31/2",
  "product": "ROLNE",
  "is_active": "nie",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "Prawdopodobieństwo zalania": "123"
  }
}
```

PESEL (Produkt = null → all)

```json
{
  "id_type": "PESEL",
  "id_value": "52030478900",
  "product": "all",
  "is_active": "tak",
  "data_od": "2024-08-01",
  "data_do": "2025-08-01",
  "dane_opisowe": {
    "Notatka": "brak",
    "Ostatnia wizyta": "2025-04-15"
  }
}
```