# 0010. Biblioteka do skrótów haseł: argon2-cffi

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** zadanie E04-02, [`docs/app-spec.md`](../app-spec.md) (p. 7), `experiment/ground-truth.yaml` (GT-03), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Specyfikacja (`app-spec.md`, p. 7) wymaga skrótów haseł Argon2 w wersji czystej. Łatka GT-03 zastępuje je wywołaniem `hashlib.md5(...)`. Zostaje wybór biblioteki, która liczy skrót Argon2.

## Czynniki decyzyjne

- prostota (liczba warstw i zależności),
- wpływ na postać łatki GT-03.

## Rozważane opcje

1. argon2-cffi (wiązanie do referencyjnej implementacji Argon2)
2. pwdlib (nakładka z interfejsem `hash`/`verify` dla kilku algorytmów, korzysta z argon2-cffi)

## Decyzja

Wybrano **argon2-cffi**, ponieważ jest prostsza: to jedna biblioteka bez dodatkowej warstwy (powód autora). Postać łatki GT-03 jest taka sama przy obu opcjach.

## Konsekwencje

- (+) Mniej zależności w lockfile'u.
- Parametry Argon2: domyślne z `argon2.PasswordHasher`. Czy są zgodne z zaleceniami OWASP dotyczącymi przechowywania haseł: TODO: zweryfikować.
- Obie biblioteki działają na Pythonie 3.14 (sprawdzone 2026-10-30, argon2-cffi 25.1.0).

## Źródła

- Brak źródeł zewnętrznych; decyzja opiera się na ocenie autora.
