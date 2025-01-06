# Aplikacja_bazodanowa

# Spis Treści
1. [Opis projektu](#opis-projektu)
2. [Technologie](#technologie)
3. [Wymagania wstępne](#wymagania-wstępne)
    1. [Serwer MySQL](#11-serwer-mysql)
    2. [Instalacja zależności](#12-instalacja-zależności)
        - [Backend](#backend)
        - [Frontend](#frontend)
    3. [Instalacja dodatkowych zależności Python](#13-instalacja-dodatkowych-zależności-python)
4. [Konfiguracja aplikacji](#konfiguracja-aplikacji)
    1. [Plik konfiguracyjny](#21-plik-konfiguracyjny)
    2. [Zmiana poświadczeń](#22-zmiana-poświadczeń)
    3. [Pobieranie bazy danych z GitHub](#23-pobieranie-bazy-danych-z-github)
5. [Uruchomienie aplikacji](#uruchomienie-aplikacji)
6. [Backend Aplikacji Zarządzania Flotą](#backend-aplikacji-zarządzania-flotą)
7. [Frontend Aplikacji Zarządzania Flotą](#frontend-aplikacji-zarządzania-flotą)
8. [Endpointy API](#endpointy-api)
9. [Twórcy](#twórcy)

# Opis projektu  

Ten program został stworzony, aby pomóc użytkownikom w zarządzaniu flotą pojazdów poprzez prowadzenie dzienników serwisowych. Dzięki temu użytkownicy mogą:  

- **Zapisywać ceny i daty serwisów** - – rejestrować szczegóły dotyczące napraw i przeglądów, co umożliwia dokładną kontrolę historii serwisowej pojazdów. 
- **Monitorować koszty eksploatacyjne** – system pozwala na szczegółową analizę wydatków, co ułatwia podejmowanie decyzji dotyczących opłacalności utrzymania floty
- **Generować raporty** z możliwością filtrowania danych według różnych kryteriów, co pozwala na tworzenie przejrzystych analiz i zestawień.  

Dodatkowe funkcjonalności magazynowe:  
- **Magazyn części zamiennych** – umożliwia zarządzanie zapasami i kontrolę dostępności kluczowych elementów serwisowych.  
- **Spis wyposażenia pojazdów** – opcjonalnie pozwala przypisywać przedmioty, takie jak pasy czy zestawy kluczy, do konkretnych pojazdów (ciężarówek i naczep).  

Program stanowi kompleksowe narzędzie wspierające firmy w optymalizacji zarządzania flotą i obniżaniu kosztów operacyjnych.  

## Technologie
Aplikacja działa w wersji desktopowej.

Backend został napisany z użyciem następujących technologii i bibliotek:  

- **Python** – główny język programowania.  
- **Flask** – framework webowy używany do tworzenia API.  
- **Flask-SQLAlchemy** – ORM dla interakcji z bazą danych MySQL.  
- **MySQL** – baza danych przechowująca dane dotyczące pojazdów, kierowców, serwisów i innych elementów aplikacji.  
- **Blueprinty Flask** – do organizacji endpointów API w moduły.  
- **mysql-connector** – sterownik do łączenia się z bazą danych MySQL. 

Frontend został napisany z użyciem następujących technologii i bibliotek:
- **PyQt5** – framework do tworzenia GUI
- **PyMySQL** – klient MySQL dla Pythona
- **requests** –  biblioteka do wykonywania zapytań HTTP.

# Konfiguracja aplikacji

Aplikacja używa pliku konfiguracyjnego `config.py` do ustawienia połączenia z bazą danych MySQL.

## Plik konfiguracyjny

Skopiuj poniższy fragment do swojego pliku `config.py`, aby ustawić odpowiednią konfigurację bazy danych:

```python
class Config:
    """
    ----------------------------------- konfiguracja: Patryk -----------------------------------------
    """
    # Konfiguracja bazy danych MySQL bez użycia pliku .env
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:bazydanych123@localhost:3306/TransportManager2DB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Zmiana poświadczeń

Jeśli chcesz używać innych poświadczeń dla bazy danych, zaktualizuj wartości w konfiguracji:

- **`root`** - nazwa użytkownika bazy danych
- **`bazydanych123`** - hasło użytkownika
- **`localhost:3306`** - adres serwera i port bazy danych (domyślnie port 3306)
- **`TransportManager2DB`** - nazwa bazy danych

## Pobieranie bazy danych z GitHub

Baza danych jest dostępna w pliku SQL na GitHubie. Aby ją zaimportować:

1. Pobierz plik bazy danych z repozytorium:
    - Przejdź do [repozytorium na GitHubie](link do repozytorium).
    - Pobierz plik z bazą danych, np. `transport_manager.sql`.

2. Zaloguj się do swojego serwera MySQL i zaimportuj plik:

```bash
mysql -u root -p TransportManager2DB < transport_manager.sql
```

Zostaniesz poproszony o podanie hasła użytkownika `root`. Upewnij się, że plik SQL zawiera wszystkie niezbędne tabele i dane.

# Uruchomienie aplikacji

Po skonfigurowaniu serwera MySQL i zaimportowaniu bazy danych z GitHub, możesz uruchomić aplikację:

1. Uruchom serwer MySQL, jeśli jeszcze tego nie zrobiłeś.
2. Upewnij się, że baza danych `TransportManager2DB` została zaimportowana i jest dostępna.
3. Zainstaluj wszystkie wymagane zależności (zarówno frontendowe, jak i backendowe), uruchamiając:

```bash
pip install -r requirements_backend.txt
pip install -r requirements_frontend.txt
```

4. Uruchom aplikację za pomocą komendy:

```bash
python run.py
```

# Backend Aplikacji Zarządzania Flotą  

Backend tej aplikacji został stworzony w celu obsługi systemu zarządzania flotą pojazdów. Umożliwia komunikację z bazą danych MySQL oraz obsługę API dla operacji na pojazdach, kierowcach, serwisach i innych powiązanych danych.  

---

# Frontend Aplikacji Zarządzania Flotą  

Frontend tej aplikacji został stworzony z wykorzystaniem PyQt5, który umożliwia tworzenie graficznych interfejsów użytkownika w Pythonie. Interfejs aplikacji pozwala użytkownikom na łatwą interakcję z systemem zarządzania flotą, umożliwiając dostęp do danych o pojazdach, kierowcach, serwisach oraz innych zasobach.

Aplikacja frontendowa komunikuje się z backendem za pomocą zapytań HTTP, korzystając z biblioteki requests, która ułatwia wysyłanie żądań do API i odbieranie danych.

---

# Endpointy API

Wszystkie endpointy API znajdują się w katalogu `routes_dir`. Tam można znaleźć moduły, które definiują różne ścieżki i logikę obsługi zapytań HTTP.

## Endpointy API dla Części

### `GET /czesc/<int:id>`
- **Opis**: Pobiera szczegóły części na podstawie jej identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator części w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane części, w tym:
    - `ID części`
    - `idTypSerwisu`
    - `Typ Serwisu`
    - `Nazwa elementu`
    - `Ilość`
  - **404 Not Found**: Jeśli część o podanym identyfikatorze nie została znaleziona.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /czesci`
- **Opis**: Pobiera listę części z możliwością filtrowania i sortowania.
- **Parametry**:
  - `nazwaElementu` (string, opcjonalny): Nazwa elementu do wyszukiwania.
  - `idTypSerwisu` (int, opcjonalny): ID typu serwisu, do którego przypisana jest część.
  - `includeTypSerwisu` (string, opcjonalny): Uwzględnienie tylko części z określonym typem serwisu.
  - `excludeTypSerwisu` (string, opcjonalny): Wykluczenie części z określonym typem serwisu.
  - `sort_by` (string, opcjonalny): Kolumna do sortowania (domyślnie `nazwaElementu`).
  - `order` (string, opcjonalny): Kierunek sortowania (`asc` lub `desc`).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę części z poniższymi polami:
    - `idCzesc`
    - `idTypSerwisu`
    - `typSerwisu`
    - `nazwaElementu`
    - `ilosc`
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /czesc/add`
- **Opis**: Dodaje nową część lub aktualizuje istniejącą, zwiększając ilość.
- **Parametry w formacie json**:
  - `Nazwa elementu` (string, wymagany): Nazwa części.
  - `Ilość` (int, wymagany): Ilość części.
  - `idTypSerwisu` (int, wymagany): ID typu serwisu, do którego przypisana jest część.
- **Odpowiedzi**:
  - **201 Created**: Jeśli część została dodana lub zaktualizowana pomyślnie.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /czesc/validate`
- **Opis**: Waliduje dane wejściowe dla nowej części.
- **Parametry w formacie json**:
  - `Nazwa elementu` (string, wymagany): Nazwa części.
  - `Ilość` (int, wymagany): Ilość części.
  - `idTypSerwisu` (int, wymagany): ID typu serwisu.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane są poprawne.
  - **400 Bad Request**: Jeśli dane są niepoprawne (np. niepoprawna nazwa lub ilość).

---

### `DELETE /czesc/delete/<int:id>`
- **Opis**: Usuwa część na podstawie jej identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator części w URL.
- **Odpowiedzi**:
  - **200 OK**: Jeśli część została pomyślnie usunięta.
  - **404 Not Found**: Jeśli część o podanym identyfikatorze nie została znaleziona.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /czesc/edit/<int:id>`
- **Opis**: Edytuje dane istniejącej części na podstawie jej identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator części w URL.
- **Parametry w formacie json**:
  - `Nazwa elementu` (string, opcjonalny): Nowa nazwa części.
  - `Ilość` (int, opcjonalny): Nowa ilość części.
  - `idTypSerwisu` (int, wymagany): Nowe ID typu serwisu.
- **Odpowiedzi**:
  - **200 OK**: Jeśli część została pomyślnie zaktualizowana.
  - **404 Not Found**: Jeśli część o podanym identyfikatorze nie została znaleziona.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /czesc/check`
- **Opis**: Sprawdza, czy część o określonej nazwie i typie serwisu istnieje w bazie danych.
- **Parametry w formacie json**:
  - `Nazwa elementu` (string, wymagany): Nazwa części.
  - `idTypSerwisu` (int, wymagany): ID typu serwisu.
- **Odpowiedzi**:
  - **200 OK**: Zwraca `idCzesc` jeśli część istnieje lub `None` jeśli nie istnieje.
  - **400 Bad Request**: Jeśli nie podano wymaganych parametrów.
  - **500 Internal Server Error**: W przypadku błędu serwera.
  - 
---

### `POST /update_part_and_equipment`
- **Opis**: Aktualizuje dane części w magazynie oraz wyposażenia pojazdu. Funkcja umożliwia edycję lub usunięcie części, a także dodanie lub zaktualizowanie ilości wyposażenia przypisanego do pojazdu.
- **Parametry w formacie json**:
  - `ID Pojazdu` (int, wymagany): ID pojazdu, do którego przypisane jest wyposażenie.
  - `czesc` (dict, wymagany): Dane części do zaktualizowania:
    - `id` (int, wymagany): ID części.
    - `nazwa` (string, wymagany): Nazwa części.
    - `ilosc` (int, wymagany): Ilość części, po przypisaniu.
  - `wyposazenie` (dict, wymagany): Dane dotyczące wyposażenia pojazdu:
    - `ilosc` (int, wymagany): Ilość wyposażenia do zaktualizowania lub dodania
- **Odpowiedzi**:
  - **200 OK**: Zwraca `idCzesc` jeśli część istnieje lub `None` jeśli nie istnieje.
  - **400 Bad Request**: Jeśli brakujące są wymagane dane w zapytaniu (np. ID Pojazdu, czesc, wyposazenie).
  - **401 Bad Request**: Jeśli brak części w magazynie.
  - **500 Internal Server Error**: W przypadku błędu serwera lub bazy danych.

  
## Endpointy API dla Kierowców

### `GET /kierowca/show/<int:id>`
- **Opis**: Pobiera dane pojedynczego kierowcy na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator kierowcy w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane kierowcy, w tym:
    - `ID kierowcy`
    - `Imię`
    - `Nazwisko`
    - `Numer telefonu`
  - **404 Not Found**: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /kierowca/show/all`
- **Opis**: Pobiera listę wszystkich kierowców z bazy danych.
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę kierowców z poniższymi polami:
    - `ID kierowcy`
    - `Imię`
    - `Nazwisko`
    - `Nr telefonu`
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /kierowca/filtry`
- **Opis**: Pobiera unikalne wartości dla kolumny kierowców, na podstawie której można filtrować dane.
- **Parametry**:
  - `filtr` (string): Typ filtru, który określa kolumnę w tabeli do filtrowania.
- **Odpowiedzi**:
  - **200 OK**: Zwraca posortowaną listę unikalnych wartości w formacie JSON.
  - **400 Bad Request**: Jeśli kolumna o podanej nazwie nie istnieje.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /kierowca/show`
- **Opis**: Pobiera i sortuje kierowców na podstawie parametrów zapytania. Możliwość filtrowania, sortowania oraz wyboru kierunku sortowania.
- **Parametry (opcjonalnie)**:
  - `filter_by` (string): Filtry w formacie JSON. Domyślnie `{}`.
  - `sort_by` (string): Kolumna do sortowania. Domyślnie "ID kierowcy".
  - `order` (string): Kierunek sortowania: "asc" lub "desc". Domyślnie "asc".
- **Odpowiedzi**:
  - **200 OK**: Zwraca posortowaną listę kierowców w formacie JSON:
    - `ID kierowcy`
    - `Imię`
    - `Nazwisko`
    - `Nr telefonu`.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /kierowca/show/alltochoice`
- **Opis**: Pobiera listę kierowców w formacie przydatnym do wyświetlania w oknie wyboru (ID i imię, nazwisko, numer telefonu).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę kierowców z ID, imieniem, nazwiskiem i numerem telefonu w formacie JSON.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /kierowca/add`
- **Opis**: Dodaje nowego kierowcę do bazy danych. Oczekuje danych w formacie JSON.
- **Parametry w formacie json (wymagane)**:
  - `imie` (string): Imię kierowcy.
  - `nazwisko` (string): Nazwisko kierowcy.
  - `nrTel` (string): Numer telefonu kierowcy.
- **Odpowiedzi**:
  - **201 Created**: Jeśli kierowca został pomyślnie dodany.
  - **500 Internal Server Error**: W przypadku błędu przy dodawaniu kierowcy.

---

### `DELETE /kierowca/delete/<int:id>`
- **Opis**: Usuwa kierowcę z bazy danych na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator kierowcy, którego chcesz usunąć.
- **Odpowiedzi**:
  - **200 OK**: Jeśli kierowca został pomyślnie usunięty.
  - **404 Not Found**: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /kierowca/edit/<int:id>`
- **Opis**: Edytuje dane istniejącego kierowcy na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator kierowcy w URL.
- **Parametry w formacie json**: 
  - `imie` (string, opcjonalny): Nowe imię kierowcy.
  - `nazwisko` (string, opcjonalny): Nowe nazwisko kierowcy.
  - `nrTel` (string, opcjonalny): Nowy numer telefonu kierowcy.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane kierowcy zostały pomyślnie zaktualizowane.
  - **404 Not Found**: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu przy aktualizacji danych.

---

### `POST /kierowca/validate`
- **Opis**: Sprawdza poprawność danych kierowcy (np. numer telefonu).
- **Parametry w formacie json**:
  - `imie` (string): Imię kierowcy.
  - `nazwisko` (string): Nazwisko kierowcy.
  - `nrTel` (string): Numer telefonu kierowcy.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane są poprawne.
  - **400 Bad Request**: Jeśli dane są niepoprawne (np. zły format numeru telefonu) - informacja o błędzie zwracana.

---

### `GET /kierowca/sort`
- **Opis**: Sortuje kierowców na podstawie wybranej kolumny i kierunku sortowania.
- **Parametry**:
  - `sort_by` (string): Kolumna do sortowania. Domyślnie "ID kierowcy".
  - `order` (string): Kierunek sortowania: "asc" lub "desc". Domyślnie "asc".
- **Odpowiedzi**:
  - **200 OK**: Zwraca posortowaną listę kierowców w formacie JSON.

## Endpointy API dla Pojazdów

### `GET /pojazd/show/<int:id>`
- **Opis**: Pobiera dane pojedynczego pojazdu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator pojazdu w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane pojazdu, w tym:
    - `ID pojazdu`
    - `Marka`
    - `Model`
    - `Numer rejestracyjny`
    - `Typ pojazdu`
    - `Dodatkowe informacje`
    - `ID kierowca`
    - `Dane kierowcy`
  - **404 Not Found**: Jeśli pojazd o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /pojazd/show/all`
- **Opis**: Pobiera listę wszystkich pojazdów z bazy danych.
- **Parametry**:
  - `typPojazdu` (str, opcjonalny): Typ pojazdu, według którego chcemy filtrować wyniki (domyślnie: brak filtru).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę pojazdów z poniższymi polami:
    - `ID pojazdu`
    - `Marka`
    - `Model`
    - `Numer rejestracyjny`
    - `Typ pojazdu`
    - `Dodatkowe informacje`
    - `ID kierowca`
    - `Dane kierowcy`
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /pojazd/filtry`
- **Opis**: Pobiera unikalne wartości dla kolumny pojazdów, na podstawie której można filtrować dane.
- **Parametry**:
  - `Typ pojazdu` (str, opcjonalny): Typ pojazdu, według którego chcemy filtrować wyniki (domyślnie: brak filtru).
  - `filtr` (str, wymagany): Typ filtru, który określa kolumnę w tabeli do filtrowania.
- **Odpowiedzi**:
  - **200 OK**: Zwraca posortowaną listę unikalnych wartości w formacie JSON.
  - **400 Bad Request**: Jeśli kolumna o podanej nazwie nie istnieje.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /pojazd/show`
- **Opis**: Pobiera i sortuje pojazdy na podstawie parametrów zapytania. Możliwość filtrowania, sortowania oraz wyboru kierunku sortowania.
- **Parametry**:
  - `filter_by` (string): Filtry w formacie JSON. Domyślnie `{}`.
  - `sort_by` (string): Kolumna do sortowania. Domyślnie "ID pojazdu".
  - `order` (string): Kierunek sortowania: "asc" lub "desc". Domyślnie "asc".
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę pojazdów z poniższymi polami:
    - `ID pojazdu`
    - `Marka`
    - `Model`
    - `Numer rejestracyjny`
    - `Typ pojazdu`
    - `Dodatkowe informacje`
    - `ID kierowca`
    - `Dane kierowcy`
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /pojazd/show/alltochoice`
- **Opis**: Pobiera listę pojazdów w formacie przydatnym do wyświetlania w oknie wyboru (ID, marka, model, numer rejestracyjny).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę pojazdów z ID, marką, modelem i numerem rejestracyjnym w formacie JSON.
    - `ID`: id pojazdu
    - `data`: typPojazdu, marka, model, nr rej. 
  - **500 Internal Server Error**: W przypadku błędu przy aktualizacji danych.

---

### `POST /pojazd/add`
- **Opis**: Dodaje nowy pojazd do bazy danych. Oczekuje danych w formacie JSON.
- **Parametry w formacie JSON**:
  - `ID kierowca` (int, opcjonalny): ID kierowcy.
  - `Typ pojazdu` (string, wymagane): Typ Pojazdu (Ciągnik/Naczepa)
  - `Marka` (string, wymagane): Marka pojazdu.
  - `Model` (string, wymagane): Model pojazdu.
  - `Numer rejestracyjny` (string, wymagane): Numer rejestracyjny pojazdu.
  - `Dodatkowe informacje` (string, opcjonalne): Dodatkowe informacje.
- **Odpowiedzi**:
  - **201 Created**: Jeśli pojazd został pomyślnie dodany.
  - **500 Internal Server Error**: W przypadku błędu przy dodawaniu pojazdu.

---

### `DELETE /pojazd/delete/<int:id>`
- **Opis**: Usuwa pojazd z bazy danych na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator pojazdu, którego chcesz usunąć.
- **Odpowiedzi**:
  - **200 OK**: Jeśli pojazd został pomyślnie usunięty.
  - **404 Not Found**: Jeśli pojazd o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /pojazd/edit/<int:id>`
- **Opis**: Edytuje dane istniejącego pojazdu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator pojazdu w URL.
- **Parametry**:
  - `ID kierowca` (int, opcjonalny): ID kierowcy.
  - `Typ pojazdu` (string, opcjonalny): Nowy typ pojazdu (Ciągnik/Naczepa).
  - `Marka` (string, opcjonalny): Nowa marka pojazdu.
  - `Model` (string, opcjonalny): Nowy model pojazdu.
  - `Numer rejestracyjny` (string, opcjonalny): Nowy numer rejestracyjny pojazdu.
  - `Dodatkowe informacje` (int, opcjonalny): Nowe dodatkowe informacje.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane pojazdu zostały pomyślnie zaktualizowane.
  - **404 Not Found**: Jeśli pojazd o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu przy aktualizacji danych.

---

### `POST /pojazd/validate`
- **Opis**: Sprawdza poprawność danych pojazdu (np. numer rejestracyjny).
- **Parametry**:
  - `ID kierowca` (int, opcjonalny): ID kierowcy.
  - `Typ pojazdu` (string, wymagane): Typ Pojazdu (Ciągnik/Naczepa)
  - `Marka` (string, wymagane): Marka pojazdu.
  - `Model` (string, wymagane): Model pojazdu.
  - `Numer rejestracyjny` (string, wymagane): Numer rejestracyjny pojazdu.
  - `Dodatkowe informacje` (string, opcjonalne): Dodatkowe informacje.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane są poprawne.
  - **400 Bad Request**: Jeśli dane są niepoprawne (np. zły format numeru rejestracyjnego).

---

### `GET /pojazd/typpojazdu/<int:id>`
- **Opis**: Pobiera typ pojazdu na podstawie jego ID.
- **Parametry URL**:
  - `id` (int): ID pojazdu, którego typ ma zostać pobrany.
- **Odpowiedzi**:
  - **200 OK**: Zwraca typ pojazdu w formacie JSON:
    - `typ_pojazdu`
  - **404 Not Found**: Jeśli pojazd o podanym ID nie istnieje.
  - **500 Internal Server Error**: Jeśli wystąpił błąd podczas pobierania typu pojazdu.

## Endpointy API dla Serwisów

### `GET /serwis/show/<int:id>`
- **Opis**: Pobiera szczegóły serwisu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator serwisu w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane serwisu.
  - **404 Not Found**: Jeśli serwis o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /serwiswidok/show/<int:id>`
- **Opis**: Pobiera szczegóły serwisu widoku na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator serwisu widoku w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane serwisu widoku.
  - **404 Not Found**: Jeśli serwis widoku o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /serwiswidok/show/all`
- **Opis**: Pobiera listę wszystkich serwisów widoków.
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę serwisów widoków.
  - **404 Not Found**: Brak serwisów widoków.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /serwis/add`
- **Opis**: Dodaje nowy serwis do bazy danych.
- **Parametry**: Dane serwisu w formacie JSON.
- **Odpowiedzi**:
  - **201 Created**: Serwis został pomyślnie dodany.
  - **400 Bad Request**: Nieprawidłowy format danych.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `DELETE /serwis/delete/<int:id>`
- **Opis**: Usuwa serwis z bazy danych na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator serwisu w URL.
- **Odpowiedzi**:
  - **200 OK**: Serwis został pomyślnie usunięty.
  - **404 Not Found**: Serwis o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /serwis/edit/<int:id>`
- **Opis**: Edytuje dane serwisu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator serwisu w URL.
  - Dane serwisu w formacie JSON.
- **Odpowiedzi**:
  - **200 OK**: Serwis został zaktualizowany.
  - **404 Not Found**: Serwis o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /serwiswidok/filtry`
- **Opis**: Pobiera dostępne filtry dla serwisów widok.
- **Parametry**:
  - `filtr` (string, opcjonalny): Opcjonalny filtr do wyszukiwania po kolumnach.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dostępne filtry.
  - **400 Bad Request**: Błąd przy mapowaniu kolumny.

---

### `GET /serwiswidok/show`
- **Opis**: Pobiera serwisy widok z możliwością filtrowania i sortowania.
- **Parametry**:
  - `filter_by` (json, opcjonalny): Parametr do filtrowania danych.
  - `sort_by` (string, opcjonalny): Kolumna do sortowania (domyślnie `ID serwisu`).
  - `order` (string, opcjonalny): Kierunek sortowania (`asc` lub `desc`).
- **Odpowiedzi**:
  - **200 OK**: Zwraca przefiltrowane i posortowane serwisy.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /serwis/validate`
- **Opis**: Waliduje dane serwisu przed dodaniem lub edytowaniem.
- **Parametry**: Dane serwisu w formacie JSON.
- **Odpowiedzi**:
  - **200 OK**: Walidacja zakończona pomyślnie.
  - **400 Bad Request**: Błąd walidacji danych (np. brak wymaga

## Endpointy API dla Typów Serwisów

### `GET /typserwis/<int:id>`
- **Opis**: Pobiera szczegóły typu serwisu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator typu serwisu w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane typu serwisu.
  - **404 Not Found**: Jeśli typ serwisu o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /typserwisy`
- **Opis**: Pobiera listę wszystkich typów serwisów.
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę wszystkich typów serwisów.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /typserwis/show/alltochoice`
- **Opis**: Pobiera listę wszystkich typów serwisów w formacie przeznaczonym do wyboru (z ID i nazwą serwisu).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę typów serwisów.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /typserwis`
- **Opis**: Dodaje nowy typ serwisu do bazy danych.
- **Parametry**: Dane typu serwisu w formacie JSON.
- **Odpowiedzi**:
  - **201 Created**: Typ serwisu został pomyślnie dodany.
  - **400 Bad Request**: Nieprawidłowy format danych (np. brak `rodzajSerwisu` lub nieprawidłowy `typPojazdu`).
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `DELETE /typserwis/<int:id>`
- **Opis**: Usuwa typ serwisu z bazy danych na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator typu serwisu w URL.
- **Odpowiedzi**:
  - **200 OK**: Typ serwisu został pomyślnie usunięty.
  - **404 Not Found**: Typ serwisu o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /typserwis/<int:id>`
- **Opis**: Edytuje dane typu serwisu na podstawie jego identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator typu serwisu w URL.
  - Dane typu serwisu w formacie JSON.
- **Odpowiedzi**:
  - **200 OK**: Typ serwisu został zaktualizowany.
  - **404 Not Found**: Typ serwisu o podanym identyfikatorze nie został znaleziony.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /typserwis/show/alltochoice2`
- **Opis**: Pobiera listę wszystkich typów serwisów w formacie przeznaczonym do wyboru (ID i dane o pojazdach i rodzajach serwisów).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę typów serwisów.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /typserwis/show`
- **Opis**: Pobiera typy serwisów z możliwością filtrowania i sortowania.
- **Parametry**:
  - `filter_by` (json, opcjonalny): Parametr do filtrowania danych.
  - `sort_by` (string, opcjonalny): Kolumna do sortowania (domyślnie `ID typ serwisu`).
  - `order` (string, opcjonalny): Kierunek sortowania (`asc` lub `desc`, domyślnie `asc`).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę posortowanych typów serwisów.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

## Endpointy API dla Wyposażenia Pojazdu

### `GET /wyposazenie/show/<int:id>`
- **Opis**: Pobiera szczegóły wyposażenia pojazdu na podstawie identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator wyposażenia pojazdu w URL.
- **Odpowiedzi**:
  - **200 OK**: Zwraca dane wyposażenia:
    - `ID pojazdu`
    - `ID Wyposażenia Pojazdu`
    - `Ilość`
    - `Opis`
    - `Pojazd` - Typ pojazdu, Marka, Model, nr rejestracyjny
  - **404 Not Found**: Jeśli wyposażenie o podanym identyfikatorze nie zostało znalezione.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `GET /wyposazenie/show/all`
- **Opis**: Pobiera listę wszystkich wyposażenia pojazdów z możliwością filtrowania i sortowania.
- **Parametry**:
  - `opis` (str): (opcjonalne) Filtrowanie po opisie wyposażenia.
  - `idPojazd` (int): (opcjonalne) Filtrowanie po identyfikatorze pojazdu.
  - `sort_by` (str): (opcjonalne) Określa pole, po którym mają być posortowane wyniki (domyślnie `opis`) Możliwe wartości:
    - `opis`: Sortowanie po opisie wyposażenia.
    - `ilosc`: Sortowanie po liczbie sztuk wyposażenia.
    - `pojazd`: Sortowanie po typie, marce, modelu i numerze rejestracyjnym pojazdu.
  - `order` (str): (opcjonalne) Określa kierunek sortowania (`asc` lub `desc`, domyślnie `asc`).
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę wyposażenia pojazdów:
    - `ID pojazdu`
    - `ID Wyposażenia Pojazdu`
    - `Ilość`
    - `Opis`
    - `Pojazd` - Typ pojazdu, Marka, Model, nr rejestracyjny
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /wyposazenie/add`
- **Opis**: Dodaje nowe wyposażenie pojazdu lub aktualizuje istniejące (jeśli wyposażenie o podanym opisie i ID pojazdu już istnieje).
- **Parametry w formacie JSON (wymagane)**:
  - `ID Pojazdu` (int): Identyfikator pojazdu.
  - `Opis` (str): Opis wyposażenia pojazdu.
  - `Ilość` (int): Ilość wyposażenia.
- **Odpowiedzi**:
  - **201 Created**: Jeśli wyposażenie zostało dodane lub zaktualizowane.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /wyposazenie/validate`
- **Opis**: Waliduje dane wejściowe dla nowego wyposażenia pojazdu.
- **Parametry w formacie JSON**:
  - `Opis` (str): Opis wyposażenia.
  - `Ilość` (int): Ilość wyposażenia (musi być liczbą całkowitą większą lub równą 0).
  - `ID Pojazdu` (int): Identyfikator pojazdu.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane są poprawne.
  - **400 Bad Request**: Jeśli dane są niepoprawne (np. pusty opis, nieprawidłowa ilość, brak pojazdu).
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /wyposazenie/edit/validate`
- **Opis**: Waliduje dane wejściowe dla edycji wyposażenia pojazdu.
- **Parametry w formacie JSON**:
  - `Opis` (str): Opis wyposażenia.
  - `Ilość` (int): Ilość wyposażenia (musi być liczbą całkowitą większą lub równą 0).
  - `ID Pojazdu` (int): Identyfikator pojazdu.
- **Odpowiedzi**:
  - **200 OK**: Jeśli dane są poprawne.
  - **400 Bad Request**: Jeśli dane są niepoprawne (np. pusty opis, nieprawidłowa ilość, brak pojazdu).
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `DELETE /wyposazenie/delete/<int:id>`
- **Opis**: Usuwa wyposażenie pojazdu na podstawie identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator wyposażenia pojazdu w URL.
- **Odpowiedzi**:
  - **200 OK**: Jeśli wyposażenie zostało usunięte.
  - **404 Not Found**: Jeśli wyposażenie o podanym identyfikatorze nie zostało znalezione.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `PUT /wyposazenie/edit/<int:id>`
- **Opis**: Edytuje dane wyposażenia pojazdu na podstawie identyfikatora `id`.
- **Parametry URL**:
  - `id` (int): Identyfikator wyposażenia pojazdu w URL.
- **Parametry w formacie JSON**:
  - `ID Pojazdu` (int): Identyfikator pojazdu.
  - `Opis` (str): Opis wyposażenia.
  - `Ilość` (int): Ilość wyposażenia.
- **Odpowiedzi**:
  - **200 OK**: Jeśli wyposażenie zostało zaktualizowane.
  - **404 Not Found**: Jeśli wyposażenie o podanym identyfikatorze nie zostało znalezione.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /wyposazenie/check`
- **Opis**: Sprawdza, czy wyposażenie o podanym opisie i ID pojazdu istnieje w bazie danych.
- **Parametry w formacie JSON**:
  - `Opis` (str): Opis wyposażenia.
  - `ID Pojazdu` (int): Identyfikator pojazdu.
- **Odpowiedzi**:
  - **200 OK**: Zwraca ID wyposażenia, jeśli istnieje, lub `null`, jeśli wyposażenie nie zostało znalezione.
  - **404 Not Found**: Jeśli pojazd o podanym ID nie istnieje.
  - **400 Bad Request**: Jeśli brakuje opisu lub ID pojazdu.
  - **500 Internal Server Error**: W przypadku błędu serwera.

---

### `POST /wyposazenie/store_item`
- **Opis**: Endpoint umożliwia zapisanie danych o części oraz aktualizację wyposażenia pojazdu w jednym bloku transakcyjnym. Operacja jest atomowa — w przypadku błędu, wszystkie zmiany są wycofywane.
- **Parametry w formacie JSON (wymagane)**:
  - `czesc` (dict):
    - `idTypSerwisu` (int): Identyfikator typu serwisu, z którym związana jest część.
    - `ilosc` (int): Liczba części do dodania (jeśli część istnieje, zwiększa jej ilość).
  - `wyposazenie` (dict):
    - `idPojazd` (int): Identyfikator pojazdu.
    - `opis` (str): Opis wyposażenia pojazdu.
    - `ilosc` (int): Nowa ilość wyposażenia (jeśli ilosc <= 0, wyposażenie zostanie usunięte).
- **Odpowiedzi**:
  - **200 OK**: Zwraca ID wyposażenia, jeśli istnieje, lub `null`, jeśli wyposażenie nie zostało znalezione.
  - **404 Not Found**: Jeśli pojazd o podanym ID nie istnieje.
  - **400 Bad Request**: Jeśli brakuje opisu lub ID pojazdu.
  - **500 Internal Server Error**: W przypadku błędu serwera.

## Endpointy pomocnicze

### `GET /`
- **Opis**: Sprawdzenie, czy serwer Flask działa poprawnie.
- **Odpowiedzi**:
  - **200 OK**: Zwraca komunikat "Flask server is running!".
  
### `GET /api/columns/<table_name>`
- **Opis**: Pobiera informacje o kolumnach w tabeli na podstawie jej nazwy.
- **Parametry**:
  - `table_name` (str): Nazwa tabeli, której kolumny mają być pobrane (np. `kierowca`, `pojazd`, `czesc`, `serwiswidok`, `serwis`, `WyposazeniePojazdu`).
- **Logika**:
  - Na podstawie podanej nazwy tabeli, wybrana jest odpowiednia klasa modelu.
  - Następnie, za pomocą metody `get_columns_info()`, pobierane są informacje o kolumnach danej tabeli.
- **Odpowiedzi**:
  - **200 OK**: Zwraca listę kolumn i ich typów w formacie JSON.
  - **400 Bad Request**: Jeśli podana tabela jest nieznana.
  
# Twórcy

- **Patryk Kurt** - https://github.com/compton22
- **Grzegorz Cyba** - https://github.com/grzesiex22