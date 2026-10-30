# 0013. Klient HTTP dla `TestClient`: httpx2

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** zadanie E04-03, [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Testy API korzystają z `starlette.testclient.TestClient`, który wymaga zewnętrznego klienta HTTP. Starlette 1.10.0 (wersja w `app/uv.lock`) najpierw próbuje zaimportować `httpx2`, a gdy go nie ma, używa `httpx` i zgłasza `StarletteDeprecationWarning` z zaleceniem instalacji `httpx2` (`starlette/testclient.py`, sprawdzone 2026-10-30).

## Czynniki decyzyjne

- zgodność z zaleceniem frameworka,
- czysty wynik testów, bez ostrzeżeń.

## Rozważane opcje

1. `httpx2` (2.16.0 na PyPI, repozytorium `pydantic/httpx2`)
2. `httpx` (0.28.1 na PyPI, repozytorium `encode/httpx`)

## Decyzja

Wybrano **httpx2**, ponieważ zaleca go starlette, a testy nie zgłaszają ostrzeżenia o przestarzałym kliencie (powody autora).

## Konsekwencje

- (+) Wynik pytest bez `StarletteDeprecationWarning`, bez filtrowania ostrzeżeń w konfiguracji.
- (−) httpx2 jest nowszym i mniej znanym pakietem niż httpx.
- Pakiet trafia tylko do zależności deweloperskich, nie do obrazu aplikacji.

## Źródła

- PyPI JSON API, `https://pypi.org/pypi/httpx2/json` i `https://pypi.org/pypi/httpx/json` (sprawdzone 2026-10-30).
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
