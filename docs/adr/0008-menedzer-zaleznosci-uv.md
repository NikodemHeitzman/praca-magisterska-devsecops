# 0008. Menedżer zależności Pythona: uv

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0007](0007-wersja-pythona-aplikacji.md), zadanie E04-02, `experiment/ground-truth.yaml` (GT-07), [`docs/narzedzia.md`](../narzedzia.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Skanery SCA (pip-audit, Trivy) oceniają konkretne wersje pakietów, a łatka GT-07 przypina `jinja2==3.1.2`. Aplikacja potrzebuje więc pliku blokady wersji (lockfile), czyli zapisu dokładnej wersji i sumy kontrolnej każdego pakietu, także zależności pośrednich. Ten sam lockfile instalują komputer autora, CI i obraz Dockera, co daje odtwarzalność eksperymentu (zasada 6 w `AGENTS.md`).

## Czynniki decyzyjne

- liczba narzędzi do zainstalowania i opisania,
- czas instalacji zależności w CI (czas potoku jest mierzony w eksperymencie),
- obsługa formatu blokady przez skanery z wariantu B.

## Rozważane opcje

1. uv (`uv.lock`)
2. Poetry (`poetry.lock`)
3. pip-tools (`requirements.in` → `requirements.txt` z przypiętymi wersjami i sumami)

## Decyzja

Wybrano **uv**. Powody autora:

- **Jedno narzędzie:** uv zarządza środowiskiem, wersją Pythona, lockfile'em i uruchamianiem aplikacji, więc jest mniej do instalowania i opisywania.
- **Szybkość w CI:** szybka instalacja zależności skraca czas potoku, który jest mierzony w eksperymencie. Wielkość zysku względem pozostałych opcji: TODO: zweryfikować (nie mierzono).
- **Obsługa skanerów:** według dokumentacji Trivy obsługuje `uv.lock` (`docs/guide/coverage/language/python.md` w `aquasecurity/trivy`, sprawdzone 2026-10-30). pip-audit `--locked` obsługuje tylko `pyproject.toml` i `pylock.*.toml` (README `pypa/pip-audit`, sprawdzone 2026-10-30). Dla pip-audit wystarczy eksport do `requirements.txt` z sumami.

## Konsekwencje

- (+) Jeden plik prawdy o wersjach (`uv.lock`), który Trivy czyta bezpośrednio.
- (−) Obok `uv.lock` w repozytorium leży wyeksportowany `requirements.txt` dla pip-audit (i ewentualnie dla obrazu). CI musi sprawdzać, że oba pliki są zgodne (np. `uv lock --check` i porównanie eksportu; postać: E04-02/E07).
- (−) Łatka GT-07 zmienia `pyproject.toml`, `uv.lock` i eksport naraz. To nadal jedna zmiana logiczna w jednym PR.
- Zależności są wpisane jawnie (`fastapi`, `uvicorn`, `jinja2`, `python-multipart` i inne), bez rozszerzenia `fastapi[standard]`. To rozszerzenie wymaga `jinja2>=3.1.5` (metadane fastapi 0.162.0 na PyPI), więc łatki GT-07 nie dałoby się zainstalować.
- Wersję uv trzeba przypiąć (lokalnie i w akcji `astral-sh/setup-uv` przypiętej do SHA; wpis w `docs/narzedzia.md`). Na dzień decyzji najnowsze wydanie uv to 0.13.6 (2026-10-27).
- Autor instaluje uv lokalnie.

## Źródła

- Dokumentacja Trivy, pokrycie języka Python: https://github.com/aquasecurity/trivy/blob/main/docs/guide/coverage/language/python.md (sprawdzone 2026-10-30).
- README pip-audit: https://github.com/pypa/pip-audit (sprawdzone 2026-10-30).
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
