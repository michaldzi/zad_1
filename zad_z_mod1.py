from collections import UserDict
import re
import pickle
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def display_contacts(self, contacts):

        pass

    @abstractmethod
    def display_notes(self, notes):

        pass

    @abstractmethod
    def get_input(self, prompt):

        pass


class ConsoleInterface(UserInterface):

    def display_contacts(self, contacts):

        print("Kontakty:")
        for i, contact in enumerate(contacts, start=1):
            print(f"{i}. {contact}")

    def display_notes(self, notes):

        print("Notatki:")
        for i, note in enumerate(notes, start=1):
            print(f"{i}. {note}")

    def get_input(self, prompt):

        return input(prompt)


class Field:
    """Base class for entry fields."""

    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class PhoneNumber(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Niepoprawny numer telefonu")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(value) is not None


class EmailAddress(Field):
    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Niepoprawny adres email")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(value) is not None


class BirthDate(Field):
    def __init__(self, value):
        if not self.validate_birthdate(value):
            raise ValueError("Niepoprawna data urodzenia")
        super().__init__(value)

    @staticmethod
    def validate_birthdate(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class Address(Field):
    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(value=f"{street}, {city}, {postal_code}, {country}")


class Record:
    def __init__(self, name: Name, birthdate: BirthDate = None):
        self.id = None  # The ID will be assigned by AddressBook
        self.name = name
        self.phone_numbers = []
        self.email_addresses = []
        self.birthdate = birthdate
        self.address = None  # Add a new property to store the address

    def add_address(self, address: Address):
        """Adds an address."""
        self.address = address

    def add_phone_number(self, phone_number: PhoneNumber):
        """Adds a phone number."""
        self.phone_numbers.append(phone_number)

    def remove_phone_number(self, phone_number: PhoneNumber):
        """Removes a phone number."""
        self.phone_numbers.remove(phone_number)

    def edit_phone_number(
        self, old_phone_number: PhoneNumber, new_phone_number: PhoneNumber
    ):
        """Changes a phone number."""
        self.remove_phone_number(old_phone_number)
        self.add_phone_number(new_phone_number)

    def add_email_address(self, email_address: EmailAddress):
        """Adds an email address."""
        self.email_addresses.append(email_address)

    def remove_email_address(self, email_address: EmailAddress):
        """Removes an email address."""
        self.email_addresses.remove(email_address)

    def edit_email_address(
        self, old_email_address: EmailAddress, new_email_address: EmailAddress
    ):
        """Changes an email address."""
        self.remove_email_address(old_email_address)
        self.add_email_address(new_email_address)

    def edit_name(self, new_name: Name):
        """Changes the first and last name."""
        self.name = new_name

    def days_to_birthdate(self):
        """Returns the number of days to the next birthdate."""
        if not self.birthdate or not self.birthdate.value:
            return "Brak daty urodzenia"
        today = datetime.now()
        bday = datetime.strptime(self.birthdate.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        """Returns a string representation of the entry, including the ID."""
        phone_numbers = ", ".join(
            phone_number.value for phone_number in self.phone_numbers
        )
        email_addresses = ", ".join(
            email_address.value for email_address in self.email_addresses
        )
        birthdate_str = f", Urodziny: {self.birthdate.value}" if self.birthdate else ""
        days_to_birthdate_str = (
            f", Dni do urodzin: {self.days_to_birthdate()}" if self.birthdate else ""
        )
        address_str = f"\nAdres: {self.address.value}" if self.address else ""
        return (
            f"ID: {self.id}, Imię i nazwisko: {self.name.value}, "
            f"Numery telefonów: {phone_numbers}, Adresy email: {email_addresses}{birthdate_str}{days_to_birthdate_str}{address_str}"
        )


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1
        self.free_ids = set()

    def add_record(self, record: Record):
        """Adds an entry to the address book with ID management."""
        while self.next_id in self.data or self.next_id in self.free_ids:
            self.next_id += 1
        if self.free_ids:
            record.id = min(self.free_ids)
            self.free_ids.remove(record.id)
        else:
            record.id = self.next_id
            self.next_id += 1
        self.data[record.id] = record
        print(f"Dodano wpis z ID: {record.id}.")

    def delete_record_by_id(self):
        """Deletes a record based on ID."""
        user_input = input("Podaj ID rekordu, który chcesz usunąć: ").strip()
        record_id_str = user_input.replace("ID: ", "").strip()

        try:
            record_id = int(record_id_str)
            if record_id in self.data:
                del self.data[record_id]
                self.free_ids.add(record_id)
                print(f"Usunięto rekord o ID: {record_id}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def find_record(self, search_term):
        """Finds entries containing the exact phrase provided."""
        found_records = []
        for record in self.data.values():
            if search_term.lower() in record.name.value.lower():
                found_records.append(record)
                continue
            for phone_number in record.phone_numbers:
                if search_term in phone_number.value:
                    found_records.append(record)
                    break
            for email_address in record.email_addresses:
                if search_term in email_address.value:
                    found_records.append(record)
                    break
        return found_records

    def find_records_by_name(self, name):
        """Finds records that match the given name and surname."""
        matching_records = []
        for record_id, record in self.data.items():
            if name.lower() in record.name.value.lower():
                matching_records.append((record_id, record))
        return matching_records

    def upcoming_birthdays(self, days):
        today = datetime.now().date()
        days = int(days)
        print(today)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthdate:

                bday = datetime.strptime(record.birthdate.value, "%Y-%m-%d").date()
                print(bday)
                next_birthday = bday.replace(year=today.year)
                if today > next_birthday:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                days_to = (next_birthday - today).days
                print(days_to)
                if (next_birthday - today).days <= days:
                    upcoming_birthdays.append(record.name.value)

        element = ", ".join(upcoming_birthdays)
        print(f"W ciągu najblizszych {days} dni, urodziny mają: \n{element}")

    def delete_record(self):
        """Deletes the record based on the selected ID after searching by name."""
        name_to_delete = input("Podaj imię i nazwisko osoby, którą chcesz usunąć: ")
        matching_records = self.find_records_by_name(name_to_delete)

        if not matching_records:
            print("Nie znaleziono pasujących rekordów.")
            return

        print("Znaleziono następujące pasujące rekordy:")
        for record_id, record in matching_records:
            print(f"ID: {record_id}, Rekord: {record}")

        try:
            record_id_to_delete = int(input("Podaj ID rekordu, który chcesz usunąć: "))
            if record_id_to_delete in self.data:
                del self.data[record_id_to_delete]
                self.free_ids.add(
                    record_id_to_delete
                )  # Add the ID back to the free ID pool
                print(f"Usunięto rekord o ID: {record_id_to_delete}.")
            else:
                print("Nie znaleziono rekordu o podanym ID.")
        except ValueError:
            print("Nieprawidłowe ID. Proszę podać liczbę.")

    def show_all_records(self):
        """Displays all entries in the address book."""
        if not self.data:
            print("Książka adresowa jest pusta.")
            return
        for name, record in self.data.items():
            print(record)

    def __iter__(self):
        """Returns an iterator over the address book records."""
        self.current = 0
        return self

    def __next__(self):
        if self.current < len(self.data):
            records = list(self.data.values())[self.current : self.current + 5]
            self.current += 5
            return records
        else:
            raise StopIteration


def edit_record(book):
    """Edits an existing record in the address book."""
    name_to_edit = input("Wprowadź imię i nazwisko które chcesz edytować: ")
    if name_to_edit in book.data:
        record = book.data[name_to_edit]
        print(f"Edytowanie: {name_to_edit}.")

        # Name and surname edit
        new_name_input = input(
            "Podaj imię i nazwisko (wciśnij Enter żeby zachować obecne): "
        )
        if new_name_input.strip():
            record.edit_name(Name(new_name_input))
            print("Zaktualizowano imię i nazwisko.")

        # Phone number edit
        if record.phone_numbers:
            print("Obecne numery telefonów: ")
            for idx, phone_number in enumerate(record.phone_numbers, start=1):
                print(f"{idx}. {phone_number.value}")
            phone_to_edit = input(
                "Wprowadź indeks numeru telefonu który chcesz edytować "
                "(wciśnij Enter żeby zachować obecny): "
            )
            if phone_to_edit.isdigit():
                idx = int(phone_to_edit) - 1
                if 0 <= idx < len(record.phone_numbers):
                    new_phone_number = input("Podaj nowy numer telefonu: ")
                    if new_phone_number.strip():
                        record.edit_phone_number(
                            record.phone_numbers[idx], PhoneNumber(new_phone_number)
                        )
                        print("Numer telefonu zaktualizowany.")
                    else:
                        print("Nie dokonano zmian.")
                else:
                    print("Niepoprawny indeks numeru.")
            else:
                print("Pomięto edycję numeru.")
        else:
            print("Brak numerów telefonu.")

        # E-mail edit
        if record.email_addresses:
            print("Obecne adresy e-mail: ")
            for idx, email_address in enumerate(record.email_addresses, start=1):
                print(f"{idx}. {email_address.value}")
            email_to_edit = input(
                "Wprowadź indeks adresu e-mail, który chcesz edytować "
                "(wciśnij Enter, aby zachować obecny): "
            )
            if email_to_edit.isdigit():
                idx = int(email_to_edit) - 1
                if 0 <= idx < len(record.email_addresses):
                    new_email = input("Podaj nowy adres e-mail: ")
                    if new_email.strip():
                        record.edit_email_address(
                            record.email_addresses[idx], EmailAddress(new_email)
                        )
                        print("Adres e-mail zaktualizowany.")
                    else:
                        print("Nie dokonano zmian.")
                else:
                    print("Niepoprawny indeks adresu e-mail.")
            else:
                print("Pomięto edycję adresu e-mail.")
        else:
            print("Brak adresów e-mail.")

        print("Wpis zaktualizowany.")
    else:
        print("Wpisu nie znaleziono.")


def save_address_book(book, filename="address_book.pkl"):
    try:
        with open(filename, "wb") as file:
            pickle.dump(book.data, file)
    except Exception as e:
        print(f"Błąd przy zapisie książki adresowej: {e}")


def load_address_book(filename="address_book.pkl"):
    try:
        with open(filename, "rb") as file:
            data = pickle.load(file)
        book = AddressBook()
        book.data = data
        return book
    except FileNotFoundError:
        print("Plik nie istnieje, tworzenie nowej książki adresowej.")
        return AddressBook()
    except Exception as e:
        print(f"Błąd przy ładowaniu książki adresowej: {e}")
        return AddressBook()


def input_phone_number():
    """Asks the user to enter a phone number."""
    while True:
        try:
            number = input(
                "Podaj numer telefonu w formacie '123456789' (naciśnij Enter, aby pominąć): "
            )
            if not number:
                return None
            return PhoneNumber(number)
        except ValueError as e:
            print(e)


def input_email_address():
    """Asks the user to enter an email address."""
    while True:
        try:
            address = input("Podaj adres email (naciśnij Enter, aby pominąć): ")
            if not address:
                return None
            return EmailAddress(address)
        except ValueError as e:
            print(e)


def create_record():
    """Creates an entry in the address book based on user input."""
    name_input = input("Podaj imię i nazwisko: ")
    name = Name(name_input)

    birthdate = None
    while True:
        birthdate_input = input(
            "Podaj datę urodzenia (YYYY-MM-DD) lub wciśnij Enter, aby pominąć: "
        )
        if not birthdate_input:
            break
        try:
            birthdate = BirthDate(birthdate_input)
            break
        except ValueError as e:
            print(e)

    record = Record(name, birthdate)

    while True:
        try:
            phone_number_input = input(
                "Podaj numer telefonu (lub wciśnij Enter, aby zakończyć dodawanie numerów): "
            )
            if not phone_number_input:
                break
            phone_number = PhoneNumber(phone_number_input)
            record.add_phone_number(phone_number)
        except ValueError as e:
            print(e)

    while True:
        try:
            email_address_input = input(
                "Podaj adres email (lub wciśnij Enter, aby zakończyć dodawanie adresów email): "
            )
            if not email_address_input:
                break
            email_address = EmailAddress(email_address_input)
            record.add_email_address(email_address)
        except ValueError as e:
            print(e)

    # New functionality: Adding an address
    add_address = input("Czy chcesz dodać adres? (t/n): ").lower().strip()
    if add_address in ["t"]:
        street = input("Podaj ulicę: ")
        city = input("Podaj miasto: ")
        postal_code = input("Podaj kod pocztowy: ")
        country = input("Podaj nazwę państwa: ")
        address = Address(street, city, postal_code, country)
        record.add_address(address)

    return record


class Note:
    def __init__(self, content):
        self.content = content
        self.created_at = datetime.now()
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    def __str__(self):
        return f"Data dodania: {self.created_at},\nNotatka: {self.content}"


class Notebook:
    def __init__(self):
        self.notes = []
        # A list for storing notes, each note can be a dictionary or a class instance

    def add_note(self, note_content):
        note = Note(note_content)
        self.notes.append(note)
        print("Notatka dodana.")

    def show_notes(self):
        if not self.notes:
            print("Nie ma notatek do wyświetlenia.")
        else:
            print("Twoje notatki:")
            for i, note in enumerate(self.notes, start=1):
                print(f"{i}. {note},\nTagi: {', '.join(note.tags)}")

    def delete_note(self, note_id):
        # Deleting a note
        if 1 <= note_id <= len(self.notes):
            del self.notes[note_id - 1]
            print(f"Usunięto notatkę: {note_id}")
        else:
            print("Nie ma notatki o podanym ID.")

    def save_notes(self, filename="notes.pkl"):
        try:
            with open(filename, "wb") as file:
                pickle.dump(self.notes, file)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu notatek: {e}")

    def load_notes(self, filename="notes.pkl"):
        try:
            with open(filename, "rb") as file:
                self.notes = pickle.load(file)
        except FileNotFoundError:
            print("Plik z notatkami nie istnieje. Tworzenie nowego pliku.")
            self.notes = []
        except Exception as e:
            print(f"Wystąpił błąd podczas wczytywania notatek: {e}")


class Tag:
    def __init__(self, notes):
        self.notes = notes

    def add_tag(self, note_index, tag):
        if 1 <= note_index <= len(self.notes.notes):
            note = self.notes.notes[note_index - 1]
            note.add_tag(tag)
            print(f"Do notatki dodano tag: {tag}")
        else:
            print("Nieprawidłowy numer notatki.")

    def search_tag(self, tag):
        notes_with_tag = []
        for note in self.notes.notes:
            if tag in note.tags:
                notes_with_tag.append(note)
        return notes_with_tag

    def sort_tags(self):
        sorted_dict = {}
        all_tags = set(tag for note in self.notes.notes for tag in note.tags)

        for tag in sorted(all_tags):
            sorted_dict[tag] = [note for note in self.notes.notes if tag in note.tags]

        return sorted_dict


class AssistantBot:
    def __init__(self, user_interface):
        self.ui = user_interface
        self.notebook = Notebook()
        self.notebook.load_notes()
        self.book = load_address_book()
        self.tag_manager = Tag(self.notebook)

    def main(self):
        while True:
            action = self.ui.get_input(
                "Witaj w Osobistym Asystencie proszę wybrać akcje :"
                "\n Aby wybrać kontatkty wciśnij (1),"
                "\n Aby wybrać notatki (2), "
                "\n Wyjście (3): "
            )
            if action == "1":
                while True:
                    contact_action = self.ui.get_input(
                        "Wybierz działanie: \nDodaj kontakt (1), \nZnajdź kontakt (2), "
                        "\nUsuń kontakt (3), \nEdytuj kontakt (4), \nPokaż wszystkie (5), \nWyświetl kontakty które mają najblizsze urodziny(6):  \nWróć (7): "
                    )
                    if contact_action == "1":
                        record = create_record()
                        self.book.add_record(record)
                        self.ui.display_message("Dodano kontakt.")
                    elif contact_action == "2":
                        search_term = self.ui.get_input("Wpisz szukaną frazę: ")
                        found = self.book.find_record(search_term)
                        self.ui.display_contacts(found)
                    elif contact_action == "3":
                        self.book.delete_record_by_id()
                        self.ui.display_message("Usunięto kontakt.")
                    elif contact_action == "4":
                        edit_record(self.book)
                        self.ui.display_message("Zaktualizowano kontakt.")
                    elif contact_action == "5":
                        self.ui.display_contacts(self.book.data.values())
                    elif contact_action == "6":
                        date = int(
                            self.ui.get_input(
                                "Wpisz ilość dni w której należy wyszukać:"
                            )
                        )
                        self.book.upcoming_birthdays(date)
                    elif contact_action == "7":
                        break
            elif action == "2":
                while True:
                    notes_action = self.ui.get_input(
                        "Wybierz działanie:\n1. Dodaj notatkę\n2. Wyświetl notatki\n3. Edytuj notatkę\n4. Usuń notatkę\n5. Zapisz notatki\n6. Wczytaj notatki\n7. Dodaj tag do notatki\n8. Znajdź notatkę po tagu\n9. Posortuj notatki według tagów\n0. Powrót\n"
                    )

                    if notes_action == "1":
                        note_content = self.ui.get_input("Wprowadź treść notatki: ")
                        self.notebook.add_note(note_content)
                        self.ui.display_notes("Notatka dodana.")
                    elif notes_action == "2":
                        self.ui.display_notes(self.notebook.notes)
                    elif notes_action == "3":
                        pass
                    elif notes_action == "4":
                        self.notebook.show_notes()
                        note_id = int(
                            self.ui.get_input("Podaj numer notatki do usunięcia: ")
                        )
                        self.notebook.delete_note(note_id)
                    elif notes_action == "5":
                        self.notebook.save_notes()
                        print("Notatki zostały zapisane")
                    elif notes_action == "6":
                        self.notebook.load_notes()
                        print("Notatki zaostały wczytane")
                    elif notes_action == "7":
                        self.notebook.show_notes()
                        note_index = int(
                            input("Podaj numer notatki, do której chcesz dodać tag: ")
                        )
                        tag_content = input("Wprowadź tag: ")
                        self.tag_manager.add_tag(note_index, tag_content)
                    elif notes_action == "8":
                        tag_to_search = input("Wprowadź tag do wyszukania: ")
                        notes_with_tag = self.tag_manager.search_tag(tag_to_search)
                        print(f"Notatki z tagiem '{tag_to_search}':")
                        for i, note in enumerate(notes_with_tag, start=1):
                            print(f"{i}. {note}")
                    elif notes_action == "9":
                        sorted_tags = self.tag_manager.sort_tags()
                        for tag, notes in sorted_tags.items():
                            print(f"Tag: {tag}, Notatki:")
                            for i, note in enumerate(notes, start=1):
                                print(f"  {i}. {note}")
                    elif notes_action == "0":
                        break
                    else:
                        print("Nieprawidłowy wybór. Spróbuj ponownie.")

            elif action == "3":
                print("Wyjście z programu.")
                break
            else:
                print("Nie ma takiego polecenia, wybierz jeszcze raz")

        save_address_book(self.book)
        self.notebook.save_notes()


if __name__ == "__main__":

    console_interface = ConsoleInterface()
    assistant_bot = AssistantBot(console_interface)
    assistant_bot.main()
