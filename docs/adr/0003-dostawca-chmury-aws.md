# 0003. Dostawca chmury: AWS

- **Status:** przyjęty
- **Data:** 2026-10-01
- **Decydujący:** autor pracy
- **Powiązane:** [0002](0002-konteneryzacja-docker.md), zadanie E01-09 (region: E01-07), [dziennik 2026-10-01](../log/2026-10-01.md)

## Kontekst

Aplikacja ma być wdrażana do chmury publicznej, a potok DevSecOps ma obejmować też etap wdrożenia. Projekt nie ma budżetu, więc liczą się darmowe limity. Chmura AWS jest wymieniona w tytule pracy.

## Czynniki decyzyjne

- pozycja dostawcy na rynku i dostępność materiałów (dokumentacja, kursy, przykłady),
- darmowe limity (*free tier*),
- znajomość dostawcy i wygoda pracy autora z jego konsolą i usługami.

## Rozważane opcje

1. Amazon Web Services (AWS)
2. Microsoft Azure
3. Google Cloud Platform

## Decyzja

Wybrano **AWS**, ponieważ:

- jest obecnie wiodącym dostawcą chmury publicznej i ma najwięcej materiałów do nauki i rozwiązywania problemów, <!-- TODO: zweryfikować udział w rynku w źródle branżowym -->
- według oceny autora ma najkorzystniejszy darmowy pakiet (*free tier*) spośród rozważanych dostawców. <!-- TODO: zweryfikować w aktualnych warunkach AWS i Azure -->

Azure odpadł, bo autorowi pracuje się na nim nieprzyjemnie. To subiektywny powód, ale w projekcie realizowanym przez jedną osobę wygoda pracy z narzędziem przekłada się na czas realizacji.

Google Cloud Platform rozważano krótko i odrzucono, bo autor najlepiej zna AWS.

Regionu AWS ten ADR nie rozstrzyga. Wybór regionu należy do zadania E01-07.

## Konsekwencje

- (+) Duża baza dokumentacji i przykładów skraca rozwiązywanie problemów.
- (+) Projekt mieści się w darmowych limitach. <!-- TODO: zweryfikować po zaprojektowaniu infrastruktury -->
- (−) Zależność od jednego dostawcy. Infrastruktura w Terraformie będzie specyficzna dla AWS.
- (−) Darmowe limity są ograniczone w czasie lub ilości. Trzeba monitorować koszty i ustawić alert budżetowy.
- Uwierzytelnianie potoku do AWS idzie przez OIDC, bez długoterminowych kluczy (konwencja z `AGENTS.md`, wynika też z [0004](0004-publiczne-repozytorium.md)).
- Wybór konkretnych usług (np. do uruchamiania kontenerów) i regionu dostanie osobne ADR-y.

## Źródła

- TODO: zweryfikować; źródło udziału w rynku chmury publicznej (raport branżowy), aktualne warunki AWS Free Tier i Azure Free Account; dodać do rejestru źródeł.
