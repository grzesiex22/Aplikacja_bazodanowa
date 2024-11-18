from Aplikacja_bazodanowa.backend.database import db
import re
import json
from enum import Enum
from flask import Flask, jsonify

# # Custom encoder for Enum
# class EnumEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Enum):
#             return obj.name  # or obj.value if you want the value instead
#         return super(EnumEncoder, self).default(obj)
#
# app = Flask(__name__)
#
# @app.before_request
# def set_custom_json_encoder():
#     app.json_encoder = EnumEncoder
#
class TypPojazdu(Enum):
    Ciągnik = 'Ciągnik'
    Naczepa = 'Naczepa'


class BaseModel(db.Model):
    __abstract__ = True  # Określamy klasę jako abstrakcyjną (nie będzie tworzona tabela w bazie)

    """
    Opis słownika COLUMN_NAME_MAP:
    Jest to mapa konfiguracji kolumn, w której każda kolumna jest reprezentowana przez słownik 
    zawierający różne właściwości, które mogą być używane do konfigurowania interfejsu użytkownika, walidacji, 
    edycji danych oraz filtrowania. 
    
    Oto poszczególne elementy, które zawiera każdy wpis w słowniku COLUMN_NAME_MAP:
    
    1. 'friendly_name' (string):
       - To przyjazna nazwa wyświetlana w interfejsie użytkownika (np. "ID pojazdu", "Marka").
       - Możesz zmienić ten tekst, aby lepiej pasował do kontekstu aplikacji.
       - Wartość ta jest wykorzystywana w widoku, do wyświetlania nazwy kolumny.
       - Wartość ta jest wykorzystywana do operacji na tabeli.

    
    2. 'editable' (bool): - nie korzystamy 
       - Określa, czy dane pole jest edytowalne przez użytkownika.
       - Jeśli ustawisz na `True`, użytkownik może edytować wartość w tym polu.
       - Jeśli ustawisz na `False`, pole będzie tylko do odczytu (użytkownik nie może go zmieniać).
       - Możesz ustawić `True` dla pól, które wymagają edycji (np. "Marka", "Model"), a `False` dla pól, które 
         są tylko do wyświetlania, jak "ID pojazdu".
    
    3. 'input_type' (string):
       - Określa typ danych, które będą wyświetlane lub wprowadzane w tym polu.
       - Przykłady typów:
           - 'readonly' – oznacza, że pole jest tylko do odczytu, użytkownik nie może wprowadzać zmian.
           - 'number' – użytkownik wprowadza liczbę.
           - 'list' – pole wyświetla listę rozwijaną lub opcje do wyboru.
           - 'enum' – lista predefiniowanych opcji, które użytkownik może wybrać z dostępnych wartości (np. typy pojazdów).
       - Jeśli pole jest przeznaczone tylko do wyświetlania, należy ustawić 'readonly'.
       - Jeśli użytkownik ma wybierać z listy, ustaw `input_type` na 'list' lub 'enum' w zależności od przypadku.
    
    4. 'inputs' (string/list):
       - Dodatkowe dane potrzebne do wygenerowania opcji w przypadku pola 'list' lub 'enum'.
       - Jeśli jest to pole typu 'list' lub 'enum', to w tym miejscu należy podać źródło danych:
           - Może to być endpoint API w przypadku typu 'list', np. `'kierowca/show/alltochoice'`, który ładuje dane z serwera.
           - Może to być lista statycznych wartości w przypadku 'enum', np. `[TypPojazdu.Ciągnik, TypPojazdu.Naczepa]` dla typu pojazdu.
       - Dla pól innych niż 'list' lub 'enum', `inputs` może być puste lub nieistniejące.
    
    5. 'filter' (bool/string):
       - Określa, czy ta kolumna będzie mogła być używana do filtrowania danych w interfejsie użytkownika.
       - Może przyjmować trzy różne wartości:
           - `False` – oznacza, że filtracja jest wyłączona dla tej kolumny.
           - `'select'` – oznacza, że kolumna będzie używana do filtrowania poprzez rozwijane menu (lista wyboru).
           - `'text'` – umożliwia filtrowanie tekstowe, gdzie użytkownik wpisuje frazę do wyszukania.
       - Możesz użyć `'select'` dla pól, które mają listę wartości, np. "Marka" lub "Model", a `'text'` dla pól,
         które mają umożliwiać wyszukiwanie tekstowe, np. "Numer rejestracyjny".
    
    Przykłady jak edytować poszczególne elementy:
    - Aby zmienić nazwę wyświetlaną w UI, edytuj 'friendly_name'.
    - Pola w UI wyswietlane na podstawie klucza obcego należy skonfigurować dodatkowo w API 
    - Aby zmienić sposób wprowadzania danych, ustaw 'input_type' na odpowiedni typ (np. 'number', 'list', 'readonly').
    - Jeśli pole ma zawierać opcje z API, ustaw odpowiedni endpoint w 'inputs' dla typu 'list' lub 'enum'.
    - Aby dodać możliwość filtrowania, ustaw odpowiednią wartość w 'filter' (np. `'select'` dla listy lub `'text'` dla tekstu).
    """
    COLUMN_NAME_MAP = {}

    @classmethod
    def get_columns_info(cls):
        """Zwraca szczegółowe informacje o kolumnach z przyjaznymi nazwami oraz innymi właściwościami z COLUMN_NAME_MAP."""
        columns_info = []

        # Mapowanie rzeczywistych kolumn
        actual_columns = {col.name: col for col in cls.__table__.columns}

        for column_name, properties in cls.COLUMN_NAME_MAP.items():
            if isinstance(properties, dict):  # Upewnij się, że 'properties' to słownik
                column_info = {
                    "name" : column_name,
                    "friendly_name": properties['friendly_name'],
                    "type": str(actual_columns[column_name].type) if column_name in actual_columns else None,
                    "primary_key": actual_columns[column_name].primary_key if column_name in actual_columns else False,
                    "foreign_key": bool(
                        actual_columns[column_name].foreign_keys) if column_name in actual_columns else False,
                    "editable": properties.get("editable", True),
                    "input_type": properties.get("input_type", "text"),
                     # Obsługa "inputs" dla typu 'list'
                    "inputs": cls._serialize_inputs(properties.get("inputs"))
                        if (properties.get("input_type") == 'enum' and properties.get("inputs"))
                        else properties.get("inputs", None),
                    "filter": properties.get("filter", False)
                }
                columns_info.append(column_info)
            else:
                print(f"Warning: Unexpected format for COLUMN_NAME_MAP entry '{column_name}'.")

        return columns_info

    @staticmethod
    def _serialize_inputs(inputs):
        """Funkcja pomocnicza do serializacji enumów w polu 'inputs'."""
        if inputs:
            # Sprawdzenie, czy 'inputs' zawiera Enum
            if isinstance(inputs[0], Enum):
                return [item.name for item in inputs]  # Zwróć tylko nazwy elementów enum
            else:
                return inputs
        return None


    @classmethod
    def get_column_map(cls):
        """
        Zwraca mapowanie nazw kolumn na przyjazne dla użytkownika nazwy
        """
        return cls.COLUMN_NAME_MAP

    @classmethod
    def get_column_label(cls, column_name):
        """
        Zwraca etykietę dla danej kolumny
        """
        return cls.COLUMN_NAME_MAP.get(column_name, column_name)


class Kierowca(BaseModel):
    __tablename__ = 'Kierowca'
    idKierowca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imie = db.Column(db.String(45), nullable=False)
    nazwisko = db.Column(db.String(45), nullable=False)
    nrTel = db.Column(db.String(12), nullable=False)
    pojazdy = db.relationship('Pojazd', backref='kierowca', lazy=True)

    # Mapa kolumn z przyjaznymi nazwami
    COLUMN_NAME_MAP = {
        'idKierowca': {
            'friendly_name': 'ID kierowcy',
            'editable': False,
            'input_type': 'readonly',
            'filter': False
        },
        'imie': {
            'friendly_name': 'Imię',
            'editable': True,
            'input_type': 'text',
            'filter': 'select'
        },
        'nazwisko': {
            'friendly_name': 'Nazwisko',
            'editable': True,
            'input_type': 'text',
            'filter': 'text'
        },
        'nrTel': {
            'friendly_name': 'Nr telefonu',
            'editable': True,
            'input_type': 'text',
            'filter': 'text'
        }
    }

    @staticmethod
    def serialize(kierowca):
        """
        Serializacja obiektu Kierowca z zamianą nazw kolumn na przyjazne.
        """
        serialized_data = {}
        for column_name, properties in Kierowca.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            value = getattr(kierowca, column_name)
            serialized_data[friendly_name] = value
        return serialized_data

    @staticmethod
    def deserialize(data):

        """
        Deserializacja danych z przyjaznymi nazwami na nazwy kolumn w bazie danych (te nie przyjazne).
        """
        deserialized_data = {}
        for column_name, properties in Kierowca.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            if friendly_name in data:
                deserialized_data[column_name] = data[friendly_name]

        return deserialized_data


    @staticmethod
    def validate_data(data):
        """
        Walidacja danych wejściowych dla Kierowcy.
        """
        print(f"Data in validation method: {data}")

        # Sprawdzanie, czy wszystkie wymagane pola są obecne i nie puste
        required_fields = ['Imię', 'Nazwisko', 'Nr telefonu']
        missing_fields = [field for field in required_fields if
                          field not in data or not data.get(field, '').strip()]

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            return {'message': f"Brak wymaganych pól: {missing_fields_str}"}, 400

        # Walidacja imienia i nazwiska
        if 'Imię' in data and not isinstance(data['Imię'], str):
            return {'message': 'Imię musi być ciągiem znaków'}, 400
        if 'Nazwisko' in data and not isinstance(data['Nazwisko'], str):
            return {'message': 'Nazwisko musi być ciągiem znaków'}, 400

        # Walidacja numeru telefonu (tylko cyfry, dokładnie 9 cyfr)
        if 'Nr telefonu' in data:
            if not re.match(r'^\d{9}$', data['Nr telefonu']):
                return {'message': 'Numer telefonu musi składać się z 9 cyfr'}, 400

        return None  # Brak błędów, walidacja przeszła pomyślnie


class Pojazd(BaseModel):
    __tablename__ = 'Pojazd'
    idPojazd = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idKierowca = db.Column(db.Integer, db.ForeignKey('Kierowca.idKierowca'), nullable=True)
    typPojazdu = db.Column(db.Enum(TypPojazdu), nullable=False)
    marka = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(45), nullable=False)
    nrRejestracyjny = db.Column(db.String(8), nullable=False)
    dodatkoweInf = db.Column(db.String(100), nullable=True)

    COLUMN_NAME_MAP = {
        'idPojazd': {
            'friendly_name': 'ID pojazdu',
            'editable': False,
            'input_type': 'readonly',
        },
        'idKierowca': {
            'friendly_name': 'ID kierowca',
            'editable': False,
            'input_type': 'Dane kierowcy',
            'filter': False
        },
        'Kierowca': {
            'friendly_name': 'Dane kierowcy',
            'editable': True,
            'input_type': 'list',
            'inputs': 'kierowca/show/alltochoice',
            'filter': 'select'
        },
        'typPojazdu': {
            'friendly_name': 'Typ pojazdu',
            'editable': True,
            'input_type': 'enum',
            'inputs': [TypPojazdu.Ciągnik, TypPojazdu.Naczepa],
            'filter': False
        },
        'marka': {
            'friendly_name': 'Marka',
            'editable': True,
            'input_type': 'text',
            'filter': 'select'
        },
        'model': {
            'friendly_name': 'Model',
            'editable': True,
            'input_type': 'text',
            'filter': 'select'
        },
        'nrRejestracyjny': {
            'friendly_name': 'Numer rejestracyjny',
            'editable': True,
            'input_type': 'text',
            'filter': 'text'
        },
        'dodatkoweInf': {
            'friendly_name': 'Dodatkowe informacje',
            'editable': True,
            'input_type': 'text',
            'filter': 'text'
        }
    }

    @staticmethod
    def serialize(pojazd):
        """
        Serializacja obiektu Pojazd z zamianą nazw kolumn na przyjazne,
        w tym ID kierowcy i jego pełne imię i nazwisko.
        """
        serialized_data = {}

        for column_name, properties in Pojazd.COLUMN_NAME_MAP.items():
            if column_name == 'Kierowca':
                # Specjalny przypadek: dodajemy imię i nazwisko kierowcy
                kierowca = Kierowca.query.get(pojazd.idKierowca) if pojazd.idKierowca else None
                serialized_data[properties[
                    'friendly_name']] = f"{kierowca.imie} {kierowca.nazwisko}, tel. {kierowca.nrTel}" if kierowca else "Brak kierowcy"
            else:
                # Standardowa serializacja
                value = getattr(pojazd, column_name)
                if column_name == 'typPojazdu' and isinstance(value, TypPojazdu):
                    # Zamiana typu Enum na jego wartość
                    serialized_data[properties['friendly_name']] = value.value
                elif column_name == 'idKierowca' and value == None:
                    serialized_data[properties['friendly_name']] = ""
                else:
                    serialized_data[properties['friendly_name']] = value

        print(f"Serialized data pojazd: {serialized_data}")
        return serialized_data


    @staticmethod
    def deserialize(data):
        """
        Deserializacja danych wejściowych z przyjaznymi nazwami do nazw kolumn w bazie danych.
        """
        deserialized_data = {}
        print(f"Before deserialization: {data}")

        for column_name, properties in Pojazd.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']

            if column_name == 'idKierowca' and friendly_name in data:
                deserialized_data[column_name] = data[friendly_name] if data[friendly_name] else None
            elif column_name == 'typPojazdu' and friendly_name in data:
                # Przekształcenie wartości typu Enum
                value = data[friendly_name]
                try:
                    # Przekształcamy wartość do odpowiedniego typu Enum
                    deserialized_data[column_name] = TypPojazdu(value)
                except ValueError:
                    return {'message': f"Nieprawidłowa wartość dla {friendly_name}: {value}"}, 400
            elif column_name == "Kierowca":
                continue  # Pomijamy "Kierowca", bo nie jest fizyczną kolumną w tabeli
            elif friendly_name in data:
                deserialized_data[column_name] = data[friendly_name]

        print(f"After deserialization: {deserialized_data}")
        return deserialized_data


    @staticmethod
    def validate_data(data):
        """
        Walidacja danych wejściowych dla Kierowcy.
        """
        print(f"Data in validation method: {data}")


        # Sprawdzanie, czy wszystkie wymagane pola są obecne i nie puste
        required_fields = ['Marka', 'Model', 'Numer rejestracyjny']
        missing_fields = [field for field in required_fields if
                          field not in data or not data.get(field, '').strip()]

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            return {'message': f"Brak wymaganych pól: {missing_fields_str}"}, 400

        # Walidacja typu pojazdu
        if 'Typ pojazdu' in data:
            typ_pojazdu = data['Typ pojazdu']

            valid_types = [typ for typ in TypPojazdu]# Korzystamy z TypPojazdu jako Enum
            print(f"Valid_types: {valid_types}")
            if typ_pojazdu not in [typ.name for typ in valid_types]:  # Typy Enum są w .name
                return {'message': f"Nieprawidłowy typ pojazdu: {typ_pojazdu}"}, 400

        # Walidacja ID kierowcy, jeśli jest obecne
        if 'ID kierowca' in data and data['ID kierowca']:
            id_kierowca = data['ID kierowca']
            kierowca = Kierowca.query.get(id_kierowca)
            if not id_kierowca:
                return {'message': f"Kierowca o ID {id_kierowca} nie istnieje."}, 400

        # Walidacja numeru rejestracyjnego (alfanumeryczny, maksymalnie 8 znaków)
        if 'Numer rejestracyjny' in data:
            nr_rejestracyjny = data['Numer rejestracyjny']
            if not re.match(r'^[A-Z0-9]{1,8}$', nr_rejestracyjny):
                return {
                    'message': 'Numer rejestracyjny musi składać się z maksymalnie 8 znaków alfanumerycznych (A-Z, 0-9).'}, 400

        return None  # Brak błędów, walidacja przeszła pomyślnie

# class TypSerwisu(BaseModel):
#     __tablename__ = 'TypSerwisu'
#     idTypSerwisu = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     rodzajSerwisu = db.Column(db.String(100), nullable=False)
#     typPojazdu = db.Column(db.Enum('Ciągnik', 'Naczepa'), nullable=False)
#
#
#     COLUMN_NAME_MAP = {
#         'rodzajSerwisu': 'Rodzaj serwisu',
#         'typPojazdu': 'Typ pojazdu'
#     }


class TypSerwisu(BaseModel):
    __tablename__ = 'TypSerwisu'
    idTypSerwisu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rodzajSerwisu = db.Column(db.String(100), nullable=False)
    typPojazdu = db.Column(db.Enum('Ciągnik', 'Naczepa'), nullable=False)

    # Mapa kolumn z przyjaznymi nazwami
    COLUMN_NAME_MAP = {
        'idTypSerwisu': {
            'friendly_name': 'ID typu serwisu',
            'editable': False,
            'input_type': 'readonly',
            'filter': False
        },
        'rodzajSerwisu': {
            'friendly_name': 'Rodzaj serwisu',
            'editable': True,
            'input_type': 'text',
            'filter': 'text'
        },
        'typPojazdu': {
            'friendly_name': 'Typ pojazdu',
            'editable': True,
            'input_type': 'select',
            'filter': 'select'
        }
    }

    @staticmethod
    def serialize(typ_serwisu):
        """
        Serializacja obiektu TypSerwisu z zamianą nazw kolumn na przyjazne.
        """
        serialized_data = {}
        for column_name, properties in TypSerwisu.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            value = getattr(typ_serwisu, column_name)
            serialized_data[friendly_name] = value
        return serialized_data

    @staticmethod
    def deserialize(data):
        """
        Deserializacja danych z przyjaznymi nazwami na nazwy kolumn w bazie danych.
        """
        deserialized_data = {}
        for column_name, properties in TypSerwisu.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            if friendly_name in data:
                deserialized_data[column_name] = data[friendly_name]
        return deserialized_data

    @staticmethod
    def validate_data(data):
        """
        Walidacja danych wejściowych dla TypSerwisu.
        """
        print(f"Data in validation method: {data}")

        # Sprawdzanie, czy wszystkie wymagane pola są obecne i nie puste
        required_fields = ['Rodzaj serwisu', 'Typ pojazdu']
        missing_fields = [field for field in required_fields if field not in data or not data.get(field, '').strip()]

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            return {'message': f"Brak wymaganych pól: {missing_fields_str}"}, 400

        # Walidacja rodzaju serwisu
        if 'Rodzaj serwisu' in data and not isinstance(data['Rodzaj serwisu'], str):
            return {'message': 'Rodzaj serwisu musi być ciągiem znaków'}, 400

        # Walidacja typu pojazdu
        if 'Typ pojazdu' in data:
            valid_typy_pojazdu = ['Ciągnik', 'Naczepa']
            if data['Typ pojazdu'] not in valid_typy_pojazdu:
                return {'message': f"Typ pojazdu musi być jednym z: {', '.join(valid_typy_pojazdu)}"}, 400

        return None  # Brak błędów, walidacja przeszła pomyślnie

class Serwis(BaseModel):
    __tablename__ = 'Serwis'
    idSerwis = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPojazd = db.Column(db.Integer, db.ForeignKey('Pojazd.idPojazd'), nullable=False)
    idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    cenaCzesciNetto = db.Column(db.Integer, nullable=True)
    robocizna = db.Column(db.Integer, nullable=True)
    kosztCalkowityNetto = db.Column(db.Integer, nullable=False)
    przebieg = db.Column(db.Integer, nullable=True)
    infoDodatkowe = db.Column(db.String(200), nullable=True)

    COLUMN_NAME_MAP = {
        'data': 'Data serwisu',
        'cenaCzesciNetto': 'Cena części netto',
        'robocizna': 'Koszt robocizny',
        'kosztCalkowityNetto': 'Koszt całkowity netto',
        'przebieg': 'Przebieg',
        'infoDodatkowe': 'Dodatkowe informacje'
    }


# class Czesc(BaseModel):
#     __tablename__ = 'Część'
#     idCzesc = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
#     nazwaElementu = db.Column(db.String(100), nullable=False)
#     ilosc = db.Column(db.Integer, nullable=False)
#
#     COLUMN_NAME_MAP = {
#         'nazwaElementu': 'Nazwa elementu',
#         'ilosc': 'Ilość'
#     }

# class Czesc(BaseModel):
#     __tablename__ = 'Część'
#
#     idCzesc = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
#     nazwaElementu = db.Column(db.String(100), nullable=False)
#     ilosc = db.Column(db.Integer, nullable=False)
#
#     # Relacje
#     typ_serwisu = db.relationship('TypSerwisu', backref='czesci', lazy=True)
#
#     # Mapa kolumn z przyjaznymi nazwami
#     COLUMN_NAME_MAP = {
#         'idCzesc': {
#             'friendly_name': 'ID części',
#             'editable': False,
#             'input_type': 'text',
#         },
#         'idTypSerwisu': {
#             'friendly_name': 'idTypSerwisu',
#             'editable': False,
#             'input_type': 'Dane Typ Serwisu',
#         },
#         'TypSerwisu': {
#             'friendly_name': 'Dane Typ serwisu',
#             'editable': True,
#             'input_type': 'list',
#             'inputs': 'typserwisu/show/alltochoice',
#         },
#
#         'nazwaElementu': {
#             'friendly_name': 'Nazwa elementu',
#             'editable': True,
#             'input_type': 'text',
#         },
#         'ilosc': {
#             'friendly_name': 'Ilość',
#             'editable': True,
#             'input_type': 'number',
#         }
#     }
#
#     @staticmethod
#     def serialize(czesc):
#         """
#         Serializacja obiektu Czesc z zamianą nazw kolumn na przyjazne.
#         """
#         serialized_data = {}
#         for column_name, properties in Czesc.COLUMN_NAME_MAP.items():
#             friendly_name = properties['friendly_name']
#             value = getattr(czesc, column_name)
#
#             # Jeśli chodzi o relację, dodajemy również szczegóły z powiązanego obiektu
#             if column_name == 'idTypSerwisu':
#                 if czesc.typ_serwisu:
#                     serialized_data[properties['friendly_name']] = czesc.typ_serwisu.rodzajSerwisu
#                 else:
#                     serialized_data[properties['friendly_name']] = None
#             else:
#                 serialized_data[friendly_name] = value
#
#         return serialized_data
#
#     @staticmethod
#     def deserialize(data):
#         """
#         Deserializacja danych z przyjaznymi nazwami na nazwy kolumn w bazie danych (te nieprzyjazne).
#         """
#         deserialized_data = {}
#
#         # Mapowanie przyjaznych nazw na kolumny
#         for column_name, properties in Czesc.COLUMN_NAME_MAP.items():
#             friendly_name = properties['friendly_name']
#             if friendly_name in data:
#                 deserialized_data[column_name] = data[friendly_name]
#
#         # Dla pola 'Dane Typ serwisu', znajdź odpowiedni `idTypSerwisu`
#         if 'Dane Typ serwisu' in data:
#             typ_serwisu_name = data['Dane Typ serwisu']
#             print(f"Deserializacja: Szukam Typ serwisu dla '{typ_serwisu_name}'")
#
#             # Zapytanie do bazy danych w celu uzyskania `idTypSerwisu`
#             try:
#                 typ_serwisu = TypSerwisu.query.filter_by(rodzajSerwisu=typ_serwisu_name).first()
#                 if typ_serwisu:
#                     deserialized_data['idTypSerwisu'] = typ_serwisu.idTypSerwisu
#                     print(f"Znaleziono idTypSerwisu: {typ_serwisu.idTypSerwisu} dla '{typ_serwisu_name}'")
#                 else:
#                     print(f"Typ serwisu o nazwie '{typ_serwisu_name}' nie istnieje w bazie danych")
#                     deserialized_data['idTypSerwisu'] = None
#             except Exception as e:
#                 print(f"Błąd podczas wyszukiwania Typ serwisu: {e}")
#                 deserialized_data['idTypSerwisu'] = None
#
#         return deserialized_data
#
#     @staticmethod
#     def validate_data(data):
#         """
#         Walidacja danych wejściowych dla Części.
#         """
#         print(f"Data in validation method: {data}")
#
#         # Sprawdzanie, czy wszystkie wymagane pola są obecne i nie puste
#         required_fields = ['Nazwa elementu', 'Ilość']
#         missing_fields = [field for field in required_fields if
#                           field not in data or not data.get(field, '').strip()]
#
#         if missing_fields:
#             missing_fields_str = ", ".join(missing_fields)
#             return {'message': f"Brak wymaganych pól: {missing_fields_str}"}, 400
#
#         # Walidacja nazwy elementu
#         if 'Nazwa elementu' in data and not isinstance(data['Nazwa elementu'], str):
#             return {'message': 'Nazwa elementu musi być ciągiem znaków'}, 400
#
#         # Walidacja ilości (liczba całkowita) - sprawdzamy, czy "Ilość" jest liczbą
#         if 'Ilość' in data:
#             try:
#                 # Jeśli "Ilość" jest ciągiem znaków, próbujemy przekonwertować go na int
#                 quantity = int(data['Ilość'])
#                 if quantity < 0:
#                     return {'message': 'Ilość musi być liczbą całkowitą większą lub równą 0'}, 400
#             except ValueError:
#                 return {'message': 'Ilość musi być liczbą całkowitą'}, 400
#
#         return None  # Brak błędów, walidacja przeszła pomyślnie

class Czesc(BaseModel):
    __tablename__ = 'Część'

    idCzesc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
    nazwaElementu = db.Column(db.String(100), nullable=False)
    ilosc = db.Column(db.Integer, nullable=False)

    # Relacje
    typ_serwisu = db.relationship('TypSerwisu', backref='czesci', lazy=True)

    # Mapa kolumn z przyjaznymi nazwami
    COLUMN_NAME_MAP = {
        'idCzesc': {
            'friendly_name': 'ID części',
            'editable': False,
            'input_type': 'text',
        },
        'idTypSerwisu': {
            'friendly_name': 'idTypSerwisu',
            'editable': False,
            'input_type': 'Dane Typ Serwisu',
        },
        'TypSerwisu': {
            'friendly_name': 'Dane Typ serwisu',
            'editable': True,
            'input_type': 'list',
            'inputs': 'typserwisu/show/alltochoice',
        },
        'nazwaElementu': {
            'friendly_name': 'Nazwa elementu',
            'editable': True,
            'input_type': 'text',
        },
        'ilosc': {
            'friendly_name': 'Ilość',
            'editable': True,
            'input_type': 'number',
        }
    }

    @staticmethod
    def serialize(czesc):
        """
        Serializacja obiektu Czesc z zamianą nazw kolumn na przyjazne.
        """
        serialized_data = {}
        for column_name, properties in Czesc.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            value = getattr(czesc, column_name)

            # Jeśli chodzi o relację, dodajemy również szczegóły z powiązanego obiektu
            if column_name == 'idTypSerwisu':
                if czesc.typ_serwisu:
                    serialized_data[properties['friendly_name']] = czesc.typ_serwisu.rodzajSerwisu
                else:
                    serialized_data[properties['friendly_name']] = None
            else:
                serialized_data[friendly_name] = value

        return serialized_data

    @staticmethod
    def deserialize(data):
        """
        Deserializacja danych z przyjaznymi nazwami na nazwy kolumn w bazie danych (te nieprzyjazne).
        """
        deserialized_data = {}

        # Mapowanie przyjaznych nazw na kolumny
        for column_name, properties in Czesc.COLUMN_NAME_MAP.items():
            friendly_name = properties['friendly_name']
            if friendly_name in data:
                deserialized_data[column_name] = data[friendly_name]

        # Dla pola 'Dane Typ serwisu', znajdź odpowiedni `idTypSerwisu`
        if 'Dane Typ serwisu' in data:
            typ_serwisu_name = data['Dane Typ serwisu']
            print(f"Deserializacja: Szukam Typ serwisu dla '{typ_serwisu_name}'")

            # Zapytanie do bazy danych w celu uzyskania `idTypSerwisu`
            try:
                typ_serwisu = TypSerwisu.query.filter_by(rodzajSerwisu=typ_serwisu_name).first()
                if typ_serwisu:
                    deserialized_data['idTypSerwisu'] = typ_serwisu.idTypSerwisu
                    print(f"Znaleziono idTypSerwisu: {typ_serwisu.idTypSerwisu} dla '{typ_serwisu_name}'")
                else:
                    print(f"Typ serwisu o nazwie '{typ_serwisu_name}' nie istnieje w bazie danych")
                    deserialized_data['idTypSerwisu'] = None
            except Exception as e:
                print(f"Błąd podczas wyszukiwania Typ serwisu: {e}")
                deserialized_data['idTypSerwisu'] = None

        return deserialized_data

    @staticmethod
    def validate_data(data):
        """
        Walidacja danych wejściowych dla Części.
        """
        print(f"Data in validation method: {data}")

        # Sprawdzanie, czy wszystkie wymagane pola są obecne i nie puste
        required_fields = ['Nazwa elementu', 'Ilość', 'Dane Typ serwisu']
        missing_fields = [field for field in required_fields if
                          field not in data or not data.get(field, '').strip()]

        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            return {'message': f"Brak wymaganych pól: {missing_fields_str}"}, 400

        # Walidacja 'Nazwa elementu' - musi być ciągiem znaków
        if 'Nazwa elementu' in data and not isinstance(data['Nazwa elementu'], str):
            return {'message': 'Nazwa elementu musi być ciągiem znaków'}, 400

        # Walidacja 'Ilość' - musi być liczbą całkowitą
        if 'Ilość' in data:
            try:
                quantity = int(data['Ilość'])
                if quantity < 0:
                    return {'message': 'Ilość musi być liczbą całkowitą większą lub równą 0'}, 400
            except ValueError:
                return {'message': 'Ilość musi być liczbą całkowitą'}, 400

        # Walidacja 'idTypSerwisu' - musi być liczbą całkowitą, jeśli jest podane
        if 'idTypSerwisu' in data:
            try:
                id_typ_serwisu = int(data['idTypSerwisu'])
                if id_typ_serwisu <= 0:
                    return {'message': 'idTypSerwisu musi być liczbą całkowitą większą od 0'}, 400
            except ValueError:
                return {'message': 'idTypSerwisu musi być liczbą całkowitą'}, 400

        # Walidacja 'Dane Typ serwisu' - sprawdzanie, czy ten typ istnieje w bazie danych
        if 'Dane Typ serwisu' in data:
            typ_serwisu_name = data['Dane Typ serwisu']
            # Sprawdzenie, czy typ serwisu o podanej nazwie istnieje w bazie danych
            typ_serwisu = TypSerwisu.query.filter_by(rodzajSerwisu=typ_serwisu_name).first()
            if not typ_serwisu:
                return {'message': f"Typ serwisu '{typ_serwisu_name}' nie istnieje w bazie danych"}, 400

        return None  # Brak błędów, walidacja przeszła pomyślnie