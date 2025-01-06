from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Czesc, TypSerwisu, WyposazeniePojazdu
from sqlalchemy.exc import SQLAlchemyError

# Blueprint dla Części
czesc_bp = Blueprint('czesc', __name__)


@czesc_bp.route('/czesc/<int:id>', methods=['GET'])
def pobierz_czesc(id):
    """
    Funkcja obsługuje żądanie GET pod adresem /czesc/<int:id>.
    Pobiera szczegóły części na podstawie jej identyfikatora.

    Parametr URL:
        - id (int): Identyfikator części przekazany w URL.

    Returns:
        Response:
        - 200 OK: Zwraca szczegóły części, w tym:
            - ID części
            - idTypSerwisu
            - Typ Serwisu (rodzaj serwisu i typ pojazdu)
            - Nazwa elementu
            - Ilość
        - 404 Not Found: Jeśli część o podanym identyfikatorze nie istnieje.
        - 500 Internal Server Error: W przypadku wystąpienia błędu serwera.
    """
    try:
        # Pobranie części z bazy danych na podstawie identyfikatora.
        czesc = Czesc.query.get(id)
        if czesc is None:
            # Jeśli część nie istnieje, zwróć status 404 i odpowiedni komunikat.
            return jsonify({'message': 'Część nie znaleziona'}), 404

        # Jeśli część posiada idTypSerwisu, pobierz szczegóły typu serwisu.
        typ_serwisu = TypSerwisu.query.get(czesc.idTypSerwisu) if czesc.idTypSerwisu else None

        # Jeśli typ serwisu istnieje, przypisz jego szczegóły; w przeciwnym razie użyj wartości domyślnych.
        typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"
        typ_serwisu_pojazd = typ_serwisu.typPojazdu if typ_serwisu else ""

        # Przygotowanie odpowiedzi z danymi części i typu serwisu.
        return jsonify({
            'ID części': czesc.idCzesc,
            'idTypSerwisu': czesc.idTypSerwisu,
            'Typ Serwisu': f"{typ_serwisu_pojazd}, {typ_serwisu_nazwa}",
            'Nazwa elementu': czesc.nazwaElementu,
            'Ilość': czesc.ilosc
        }), 200
    except Exception as e:
        # Obsłuż wszystkie nieprzewidziane błędy i zwróć status 500.
        return jsonify({'error': str(e)}), 500


@czesc_bp.route('/czesci', methods=['GET'])
def pobierz_wszystkie_czesci():
    """
    Funkcja obsługuje żądanie GET pod adresem /czesci.
    Umożliwia pobranie listy części z możliwością wyszukiwania, filtrowania i sortowania.

    Parametry wejściowe (opcjonalne):
        - nazwaElementu (string): Nazwa elementu do wyszukiwania.
        - idTypSerwisu (int): ID typu serwisu, do którego przypisana jest część.
        - includeTypSerwisu (string): Uwzględnienie tylko części z określonym typem serwisu.
        - excludeTypSerwisu (string): Wykluczenie części z określonym typem serwisu.
        - sort_by (string): Kolumna do sortowania (domyślnie `nazwaElementu`).
        - order (string): Kierunek sortowania (`asc` lub `desc`).

    Returns:
        Response:
        - 200 OK: Zwraca listę części z ich szczegółami:
            - ID części
            - idTypSerwisu
            - Typ Serwisu (rodzaj serwisu i typ pojazdu)
            - Nazwa elementu
            - Ilość.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        # Pobieranie parametrów z zapytania
        nazwa_elementu = request.args.get('nazwaElementu', '').strip()
        id_typ_serwisu = request.args.get('idTypSerwisu', None)
        include_typ_serwisu = request.args.get('includeTypSerwisu', None)
        exclude_typ_serwisu = request.args.get('excludeTypSerwisu', None)
        sort_by = request.args.get('sort_by', 'nazwaElementu')  # Domyślne sortowanie po nazwie elementu
        order = request.args.get('order', 'asc')  # Domyślnie sortowanie rosnące

        # Inicjalizacja podstawowego zapytania SQLAlchemy
        query = Czesc.query

        # Filtrowanie po nazwie elementu, jeśli podano 'nazwaElementu'
        if nazwa_elementu:
            query = query.filter(Czesc.nazwaElementu.ilike(f'%{nazwa_elementu}%'))

        # Filtrowanie po typie serwisu, jeśli podano 'idTypSerwisu'
        if id_typ_serwisu:
            query = query.filter(Czesc.idTypSerwisu == int(id_typ_serwisu))

        # Wykluczanie części na podstawie rodzaju serwisu, jeśli podano 'excludeTypSerwisu'
        if exclude_typ_serwisu:
            # Pobranie ID typów serwisu pasujących do wykluczonej wartości
            typy_serwisu = TypSerwisu.query.filter(TypSerwisu.rodzajSerwisu.ilike(f'%{exclude_typ_serwisu}%')).all()
            exclude_ids = [typ.idTypSerwisu for typ in typy_serwisu]
            if exclude_ids:
                query = query.filter(~Czesc.idTypSerwisu.in_(exclude_ids))

        # Uwzględnienie części na podstawie rodzaju serwisu, jeśli podano 'includeTypSerwisu'
        if include_typ_serwisu:
            typy_serwisu = TypSerwisu.query.filter(TypSerwisu.rodzajSerwisu.ilike(f'%{include_typ_serwisu}%')).all()
            include_ids = [typ.idTypSerwisu for typ in typy_serwisu]
            if include_ids:
                query = query.filter(Czesc.idTypSerwisu.in_(include_ids))

        # Sortowanie wyników, jeśli podano 'sort_by' i 'order'
        if sort_by in ['Typ Serwisu', 'nazwaElementu', 'ilosc']:
            if sort_by == 'Typ Serwisu':
                # Sortowanie po typie pojazdu i rodzaju serwisu
                query = query.join(TypSerwisu, Czesc.idTypSerwisu == TypSerwisu.idTypSerwisu)
                sort_columns = [TypSerwisu.typPojazdu, TypSerwisu.rodzajSerwisu]
            else:
                sort_columns = [getattr(Czesc, sort_by, Czesc.nazwaElementu)]
            # Zastosowanie sortowania malejącego, jeśli 'order' == 'desc'
            if order == 'desc':
                sort_columns = [col.desc() for col in sort_columns]
            query = query.order_by(*sort_columns)

        # Pobranie wyników zapytania
        czesci = query.all()

        # Przygotowanie listy wyników
        wynik = []
        for czesc in czesci:
            # Pobranie szczegółów typu serwisu na podstawie ID
            typ_serwisu = TypSerwisu.query.get(czesc.idTypSerwisu) if czesc.idTypSerwisu else None
            typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"
            typ_serwisu_pojazd = typ_serwisu.typPojazdu if typ_serwisu else ""

            # Dodanie szczegółów części do wyniku
            wynik.append({
                'idCzesc': czesc.idCzesc,
                'idTypSerwisu': czesc.idTypSerwisu,
                'typSerwisu': str(typ_serwisu_pojazd + ", " + typ_serwisu_nazwa),
                'nazwaElementu': czesc.nazwaElementu,
                'ilosc': czesc.ilosc
            })

        # Zwrócenie wyniku w formacie JSON
        return jsonify(wynik), 200

    except Exception as e:
        # Obsługa błędów serwera
        return jsonify({'error': str(e)}), 500


@czesc_bp.route('/czesc/add', methods=['POST'])
def dodaj_czesc():
    """
    Funkcja obsługuje żądanie POST pod adresem /czesc/add.
    Umożliwia dodanie nowej części lub aktualizację istniejącej, zwiększając jej ilość.

    Parametry wejściowe (w formacie JSON):
        - Nazwa elementu (string): Nazwa części (wymagane).
        - Ilość (int): Ilość części (wymagane).
        - idTypSerwisu (int): ID typu serwisu, do którego przypisana jest część (wymagane).

    Returns:
        Response:
        - 201 Created: Jeśli część została dodana lub zaktualizowana pomyślnie.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    data = request.get_json()  # Pobranie danych wejściowych w formacie JSON

    try:
        # Pobranie danych z żądania i ich wstępna walidacja
        id_typ_serwisu = int(data['idTypSerwisu'])
        nazwa_elementu = data['Nazwa elementu']
        ilosc = int(data['Ilość'])

        # Sprawdzenie, czy część o podanej nazwie i typie serwisu już istnieje w bazie
        istnieje_czesc = Czesc.query.filter_by(idTypSerwisu=id_typ_serwisu, nazwaElementu=nazwa_elementu).first()

        if istnieje_czesc:
            # Jeśli część już istnieje, zwiększ ilość
            istnieje_czesc.ilosc += ilosc
        else:
            # Jeśli część nie istnieje, utwórz nowy wpis w bazie danych
            nowa_czesc = Czesc(
                idTypSerwisu=id_typ_serwisu,
                nazwaElementu=nazwa_elementu,
                ilosc=ilosc
            )
            db.session.add(nowa_czesc)  # Dodanie nowego wpisu do sesji

        # Zatwierdzenie zmian w bazie danych
        db.session.commit()

        # Zwrócenie informacji o sukcesie operacji
        return jsonify({'message': 'Część dodana pomyślnie'}), 201

    except Exception as e:
        # W przypadku błędu wycofanie transakcji
        db.session.rollback()
        # Zwrócenie informacji o błędzie
        return jsonify({'error': str(e)}), 500


@czesc_bp.route('/czesc/validate', methods=['POST'])
def validate_czesc():
    """
    Funkcja obsługuje żądanie POST pod adresem /czesc/validate.
    Waliduje dane wejściowe dla nowej części, sprawdzając poprawność formatu i wymaganych pól.

    Parametry wejściowe (w formacie JSON):
        - Nazwa elementu (string, wymagany): Nazwa części. Musi być ciągiem znaków, nie pustym, i krótszym niż 100 znaków.
        - Ilość (int, wymagany): Ilość części. Musi być liczbą całkowitą.
        - idTypSerwisu (int, wymagany): ID typu serwisu. Wskazuje na typ serwisu, do którego przypisana jest część.

    Returns:
        Response:
        - 200 OK: Jeśli dane są poprawne.
        - 400 Bad Request: Jeśli dane są niepoprawne (np. brak wymaganych pól, niepoprawny format).
    """
    data = request.get_json()

    # Walidacja pola 'Nazwa elementu' - sprawdzenie obecności i typu
    if 'Nazwa elementu' not in data or not isinstance(data['Nazwa elementu'], str):
        return jsonify({'message': 'Nazwa elementu musi być ciągiem znaków'}), 400

    # Sprawdzenie, czy 'Nazwa elementu' nie jest pustym ciągiem
    if not data['Nazwa elementu'].strip():
        return jsonify({'message': 'Nazwa elementu nie może być pusta'}), 400

    # Sprawdzenie długości nazwy elementu
    if len(data['Nazwa elementu']) > 100:
        return jsonify({'message': 'Nazwa elementu nie może mieć więcej niż 100 znaków'}), 400

    # Walidacja pola 'Ilość' - sprawdzenie obecności i typu
    if 'Ilość' not in data or not isinstance(data['Ilość'], int):
        return jsonify({'message': 'Ilość musi być liczbą całkowitą'}), 400

    # Walidacja pola 'idTypSerwisu' - sprawdzenie obecności
    if 'idTypSerwisu' not in data:
        return jsonify({'message': 'Wybierz typ serwisu'}), 400

    # Jeśli wszystkie dane są poprawne, zwróć odpowiedź sukcesu
    return jsonify({'message': 'Dane są poprawne'}), 200


@czesc_bp.route('/czesc/delete/<int:id>', methods=['DELETE'])
def usun_czesc(id):
    """
    Funkcja obsługuje żądanie DELETE pod adresem /czesc/delete/<int:id>.
    Umożliwia usunięcie części z bazy danych na podstawie podanego identyfikatora.

    Parametry wejściowe:
        - id (int, wymagany): Identyfikator części przekazany w URL.

    Returns:
        Response:
        - 200 OK: Jeśli część została pomyślnie usunięta.
        - 404 Not Found: Jeśli część o podanym identyfikatorze nie została znaleziona w bazie.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        # Pobranie części na podstawie ID
        czesc = Czesc.query.get(id)

        # Sprawdzenie, czy część istnieje
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404

        # Usunięcie części z bazy danych
        db.session.delete(czesc)
        db.session.commit()

        # Zwrot odpowiedzi o pomyślnym usunięciu
        return jsonify({'message': 'Część usunięta pomyślnie'}), 200

    except Exception as e:
        # W przypadku błędu wycofanie transakcji i zwrot informacji o błędzie
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@czesc_bp.route('/czesc/edit/<int:id>', methods=['PUT'])
def edytuj_czesc(id):
    """
    Funkcja obsługuje żądanie PUT pod adresem /czesc/edit/<int:id>.
    Umożliwia edycję danych istniejącej części w bazie na podstawie podanego identyfikatora.

    Parametry URL:
        - id (int, wymagany): Identyfikator części przekazany w URL.
    Parametry wejściowe (w formacie JSON):
        - Nazwa elementu (string, opcjonalny): Nowa nazwa części (jeśli podana).
        - Ilość (int, opcjonalny): Nowa ilość części (jeśli podana).
        - idTypSerwisu (int, wymagany): Nowe ID typu serwisu, z którym część ma być powiązana.

    Returns:
        Response:
        - 200 OK: Jeśli część została pomyślnie zaktualizowana.
        - 404 Not Found: Jeśli część o podanym identyfikatorze nie została znaleziona.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    data = request.get_json()

    try:
        # Pobranie obiektu Czesc na podstawie ID
        czesc = Czesc.query.get(id)

        # Sprawdzenie, czy część istnieje
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404

        # Aktualizacja powiązania z typem serwisu
        id_typ_serwisu = int(data['idTypSerwisu'])
        czesc.idTypSerwisu = id_typ_serwisu

        # Aktualizacja pozostałych pól, jeśli są obecne w danych wejściowych
        czesc.nazwaElementu = data.get('Nazwa elementu', czesc.nazwaElementu)
        czesc.ilosc = data.get('Ilość', czesc.ilosc)

        # Zapisanie zmian w bazie danych
        db.session.commit()

        # Zwrot informacji o pomyślnym zakończeniu operacji
        return jsonify({'message': 'Część zaktualizowana pomyślnie'}), 200

    except Exception as e:
        # Wycofanie transakcji w przypadku błędu
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@czesc_bp.route('/czesc/check', methods=['POST'])
def sprawdz_czesc():
    """
    Funkcja obsługuje żądanie POST pod adresem /czesc/check.
    Umożliwia sprawdzenie, czy część o podanej nazwie i typie serwisu istnieje w bazie danych.

    Parametry wejściowe (w formacie JSON):
        - Nazwa elementu (string, wymagany): Nazwa części.
        - idTypSerwisu (int, wymagany): ID typu serwisu.

    Returns:
        Response:
        - 200 OK: Jeśli część istnieje, zwraca jej identyfikator `idCzesc`.
                  Jeśli nie istnieje, zwraca `idCzesc: None`.
        - 400 Bad Request: Jeśli brakuje wymaganych parametrów w zapytaniu.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        data = request.get_json()

        # Walidacja danych wejściowych
        if 'Nazwa elementu' not in data or 'idTypSerwisu' not in data:
            return jsonify({'error': 'Nazwa elementu i idTypSerwisu są wymagane'}), 400

        nazwa = data['Nazwa elementu']
        id_typ_serwisu = data['idTypSerwisu']

        # Wyszukiwanie części w bazie danych
        czesc = Czesc.query.filter_by(nazwaElementu=nazwa, idTypSerwisu=id_typ_serwisu).first()

        # Zwracanie wyniku
        if czesc:
            return jsonify({'idCzesc': czesc.idCzesc}), 200
        else:
            return jsonify({'idCzesc': None}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@czesc_bp.route('/update_part_and_equipment', methods=['POST'])
def update_part_and_equipment():
    """
    Funkcja obsługuje żądanie POST pod adresem /update_part_and_equipment.
    Umożliwia jednoczesną edycję lub usunięcie części w magazynie oraz aktualizację wyposażenia pojazdu.

    Parametry wejściowe (w formacie JSON):
        - ID Pojazdu (int, wymagany): ID pojazdu, do którego przypisane jest wyposażenie.
        - czesc (dict, wymagany): Słownik zawierający dane części, które mają zostać zaktualizowane:
            - id (int, wymagany): ID części.
            - nazwa (string, wymagany): Nazwa części.
            - ilosc (int, wymagany): Ilość części jaka zostanie.
        - wyposazenie (dict, wymagany): Słownik zawierający dane wyposażenia pojazdu:
            - ilosc (int, wymagany): Ilość przypisaną do pojazdu.

    Returns:
        Response:
        - 200 OK: Jeśli operacja zakończy się sukcesem, zwróci komunikat o pomyślnym zaktualizowaniu części i wyposażenia pojazdu.
        - 400 Bad Request: Jeśli brakuje wymaganych parametrów w zapytaniu lub nie znaleziono części w magazynie.
        - 401 Bad Request: Jeśli brak części w magazynie.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """

    try:
        # Pobieranie danych z zapytania
        data = request.get_json()

        pojazd_id = data.get('ID Pojazdu')
        czesc_data = data.get('czesc')  # Informacje o części
        wyposazenie_data = data.get('wyposazenie')  # Informacje o wyposazeniuPojazdu

        if not pojazd_id or not czesc_data or not wyposazenie_data:
            return jsonify({"error": "Brak wymaganych danych"}), 400

        # Rozpoczynamy transakcję
        with db.session.begin():  # Rozpoczynamy transakcję
            # Edycja/usuwanie części (Czesc)
            czesc = Czesc.query.filter_by(idCzesc=czesc_data['id']).first()
            if czesc:
                if czesc_data['ilosc'] > 0:
                    czesc.ilosc = czesc_data['ilosc']
                else:
                    db.session.delete(czesc)
            else:
                return jsonify({"error": "Brak części w magazynie"}), 401

            # Edycja lub dodanie w WyposazeniePojazdu
            wyposazenie = WyposazeniePojazdu.query.filter_by(idPojazd=pojazd_id, opis=czesc_data['nazwa']).first()
            if wyposazenie:
                wyposazenie.ilosc = wyposazenie.ilosc + wyposazenie_data['ilosc']
            else:
                wyposazenie = WyposazeniePojazdu(idPojazd=pojazd_id, opis=czesc_data['nazwa'], ilosc=wyposazenie_data['ilosc'])
                db.session.add(wyposazenie)

            # Po zakończeniu transakcji, wszystkie zmiany są zatwierdzane
            db.session.commit()

        return jsonify({"message": "Część oraz wyposażenie pojazdu zostały zaktualizowane pomyślnie."}), 200

    except SQLAlchemyError as e:
        # Jeśli wystąpił błąd w bazie danych, wycofujemy transakcję
        db.session.rollback()
        return jsonify({"error": f"Wystąpił błąd bazy danych: {str(e)}"}), 500
    except Exception as e:
        # Obsługa innych błędów
        return jsonify({"error": f"Wystąpił nieoczekiwany błąd: {str(e)}"}), 500
