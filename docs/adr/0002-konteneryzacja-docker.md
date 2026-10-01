# 0002. Konteneryzacja aplikacji: Docker

- **Status:** przyjęty
- **Data:** 2026-10-01
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), zadanie E01-09, [dziennik 2026-10-01](../log/2026-10-01.md)

## Kontekst

Aplikację webową trzeba zbudować, przetestować w potoku i wdrożyć do chmury. Potrzebny jest sposób pakowania, który daje ten sam artefakt w każdym środowisku i pozwala go skanować. Docker jest wymieniony w tytule pracy.

## Czynniki decyzyjne

- wygoda pracy: podział systemu na mniejsze, niezależne części zamiast jednego dużego pakietu,
- ten sam artefakt lokalnie, w potoku i w chmurze,
- możliwość skanowania obrazów pod kątem podatności,
- zgodność z zakresem pracy (bez orkiestracji klastrowej).

## Rozważane opcje

1. Kontenery Docker (kilka małych obrazów składanych w całość)
2. Wdrożenie bez kontenerów: jeden pakiet aplikacji instalowany bezpośrednio na maszynie wirtualnej

## Decyzja

Wybrano **kontenery Docker**, ponieważ łatwiej pracuje się na kilku małych obrazach, które składa się w całość, niż na jednym dużym pakiecie. Każdy obraz można osobno zbudować, przeskanować i wymienić.

Podział na kilka obrazów dotyczy komponentów uruchomieniowych (np. aplikacja, baza danych, serwer pośredniczący). Nie oznacza architektury mikroserwisowej, która jest poza zakresem pracy (`AGENTS.md`). Orkiestracja w Kubernetesie również jest poza zakresem. <!-- TODO: zweryfikować docelowy podział na obrazy po zaprojektowaniu aplikacji (E04) -->

## Konsekwencje

- (+) Obrazy są budowane z `Dockerfile` w repozytorium, więc środowisko uruchomieniowe jest wersjonowane i odtwarzalne.
- (+) Obraz jest osobnym artefaktem, który potok DevSecOps może skanować (podatności w warstwach systemu i zależnościach, błędy konfiguracji `Dockerfile`).
- (−) Obrazy bazowe wnoszą własne podatności. Trzeba przypinać ich wersje i regularnie je aktualizować (konwencja odtwarzalności z `AGENTS.md`).
- (−) Kilka obrazów wymaga sposobu ich łączenia i uruchamiania razem (np. Docker Compose). Ten wybór dostanie osobny ADR.
- Wybór usługi AWS do uruchamiania kontenerów należy do osobnej decyzji (po [0003](0003-dostawca-chmury-aws.md)).

## Źródła

- TODO: zweryfikować; dokumentacja Dockera i wytyczne dotyczące bezpieczeństwa kontenerów (np. OWASP Docker Security Cheat Sheet, NIST SP 800-190); dodać do rejestru źródeł.
