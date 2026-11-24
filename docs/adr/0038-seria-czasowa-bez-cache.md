# 0038. Seria czasowa bez cache w obu wariantach, przebieg rozgrzewkowy jako kontrola

- **Status:** przyjęty
- **Data:** 2026-11-20
- **Decydujący:** autor pracy
- **Powiązane:** [0035](0035-workflow-ci-lint-i-testy.md), [0036](0036-build-i-publikacja-obrazu.md), [0039](0039-skrypt-zbierajacy-czasy-potoku.md), zadanie E06-04, `experiment/PROTOCOL.md` (2.1, 2.3, K7), `docs/metodyka.md` (p. 3.2, M4, M5), [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

Protokół eksperymentu (`PROTOCOL.md`, 2.3, pkt 3, przyjęty 2026-10-13) zakłada, że w serii czasowej potoki używają cache tak jak w codziennej pracy, a przebieg rozgrzewkowy wypełnia cache przed serią. Późniejsze ADR-0035 (zależności uv) i ADR-0036 (warstwy Dockera) wyłączyły cache w wariancie A, bo czas potoku jest metryką eksperymentu. Oba dokumenty są przyjęte i sobie przeczą. Rozbieżność zgłoszono w E06-02 do rozstrzygnięcia w E06-04, przed zamrożeniem wariantu A (E06-05). Od decyzji zależy też sens przebiegu rozgrzewkowego (`PROTOCOL.md`, 2.1: 1 przebieg nieliczony i 20 pomiarowych dla każdej pary wariant–wyzwalacz).

## Czynniki decyzyjne

- porównywalność czasów między przebiegami i wariantami (M4, M5),
- trafność zewnętrzna: czy wynik odpowiada kosztowi codziennej pracy,
- prostota potoku i serii pomiarowej,
- zakres zmian w przyjętych dokumentach przed zamrożeniem wariantu A.

## Rozważane opcje

Cache w serii czasowej:

1. bez cache w obu wariantach: ADR-0035 i ADR-0036 bez zmian, protokół poprawiony
2. cache w obu wariantach, z identyczną konfiguracją dla kroków wspólnych: nowy ADR zastępuje część ADR-0035 i ADR-0036, protokół bez zmian
3. seria pomiarowa bez cache, a kilka przebiegów z cache w pilotażu, opisowo, żeby pokazać koszt braku cache

Przebieg rozgrzewkowy:

1. zostaje (1 na parę, nieliczony), jako kontrola przed serią
2. usunięty: bez cache nie ma czego rozgrzewać, a działanie sprawdza pilotaż (P5)

## Decyzja

Wybrano **serię czasową bez cache w obu wariantach (opcja 1) i przebieg rozgrzewkowy, który zostaje jako kontrola, nieliczony.** ADR-0035 i ADR-0036 zostają bez zmian. Zmienia się `PROTOCOL.md` (2.3, pkt 3 i K7). Powody autora:

- **Bez cache:**
  - porównywalność: cache dodaje zmienność zależną od tego, czy klucz trafił albo czy wpis nie wygasł,
  - prostota: nie trzeba zarządzać kluczami cache ani zakładać, że rozgrzewka go wypełni.
- **Rozgrzewka zostaje:**
  - kontrola przed serią: sprawdza, że gałąź, potok i (w serii main) wdrożenie działają, zanim zaczniemy liczyć,
  - mniejsza zmiana protokołu: układ serii (1 + 20) zostaje, zmienia się tylko uzasadnienie.

Ten sam warunek obowiązuje wariant B: kroki wspólne mają być identyczne (K2), więc wariant B też nie używa cache zależności ani warstw. Bazy podatności skanerów są osobną sprawą (P2: aktualizują się przy każdym uruchomieniu i ich wersję zapisujemy). Czy skaner pobiera bazę od zera w każdym przebiegu, czy z cache GitHub Actions, rozstrzygają ADR-y wariantu B (E07). TODO: zweryfikować w E07.

## Konsekwencje

- (+) Przyjęte ADR-0035 i ADR-0036 i workflow wariantu A się nie zmieniają.
- (+) Zmienność wyniku nie zależy od stanu cache GitHub Actions.
- (−) Wynik odpowiada kosztowi przebiegu bez cache, a nie codziennej pracy zespołu, który zwykle cache włącza. To ograniczenie trafności zewnętrznej, do opisania w 5.3. Ile cache skróciłby potok, seria nie mierzy. Pojedynczy przebieg push 44736780743 (2026-11-20, wariant A) daje rząd wielkości: instalacja zależności uv trwała po 1 s w jobach `lint` i `test`, budowanie obrazu bez cache warstw 10 s. To nie jest pomiar (TODO z ADR-0035 częściowo: koszt braku cache uv w wariancie A jest mały).
- (−) Każdy przebieg pobiera zależności i warstwy obrazu bazowego z sieci, więc czas zależy też od PyPI i rejestrów obrazów. To zmienna niekontrolowana, wspólna dla obu wariantów.
- Rozgrzewka wydłuża serię o 4 przebiegi (84 zamiast 80), z czego 2 to wdrożenia w serii main.
- `PROTOCOL.md`: 2.3, pkt 3 i wiersz K7 dostają nowe brzmienie, z odwołaniem do tego ADR.

## Źródła

- Materiał wewnętrzny: ADR-0035, ADR-0036, `experiment/PROTOCOL.md` (2.1, 2.3, K2, K7), dane przebiegu 44736780743 (`experiment/data/`, ADR-0039).
