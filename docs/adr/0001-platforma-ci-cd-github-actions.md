# 0001. Platforma CI/CD: GitHub Actions

- **Status:** przyjęty
- **Data:** 2026-10-01
- **Decydujący:** autor pracy
- **Powiązane:** [0004](0004-publiczne-repozytorium.md), zadanie E01-09, [dziennik 2026-10-01](../log/2026-10-01.md)

## Kontekst

Praca porównuje dwa potoki CI/CD: bazowy i DevSecOps. Potrzebna jest platforma, która uruchomi oba potoki na tym samym kodzie, w tych samych warunkach, i pozwoli dołączyć skanery bezpieczeństwa. Kod projektu leży na GitHubie. Platforma jest wymieniona w tytule pracy. Praca jest realizowana przez jedną osobę, więc liczy się nakład pracy potrzebny na utrzymanie samej platformy.

## Czynniki decyzyjne

- nakład pracy na utrzymanie infrastruktury CI (jedna osoba, ograniczony czas),
- integracja z repozytorium, w którym jest kod,
- koszt w ramach projektu bez budżetu,
- możliwość dołączenia skanerów bezpieczeństwa i publikowania ich wyników,
- znajomość narzędzia przez autora.

## Rozważane opcje

1. GitHub Actions
2. Jenkins
3. GitLab CI

## Decyzja

Wybrano **GitHub Actions**, ponieważ działa w tym samym serwisie, w którym jest repozytorium, i nie wymaga utrzymywania własnego serwera CI.

Jenkins odpadł, bo wymaga samodzielnego hostowania (*self-hosted*): instalacji, aktualizacji i zabezpieczenia własnego serwera. W pracy o bezpieczeństwie potoku taki serwer byłby dodatkowym elementem do utrzymania i zabezpieczenia, niezwiązanym z celem badania. Jenkinsa nie analizowano bardziej szczegółowo.

GitLab CI rozważano krótko i odrzucono, bo autor najlepiej zna GitHuba. Ta platforma dawałaby podobne możliwości, ale wymagałaby nauki nowego narzędzia bez korzyści dla celu badania.

## Konsekwencje

- (+) Brak własnej infrastruktury CI do utrzymania i zabezpieczania.
- (+) Potoki są zapisane jako pliki YAML w repozytorium (`.github/workflows/`), więc są wersjonowane razem z kodem i odtwarzalne.
- (−) Zależność od jednego dostawcy (GitHub). Przeniesienie potoków na inną platformę wymagałoby przepisania workflowów.
- (−) Akcje z GitHub Marketplace to kod stron trzecich wykonywany w potoku. Wymusza to przypinanie akcji do pełnego SHA commita (konwencja z `AGENTS.md`).
- Koszt i limity minut runnerów zależą od widoczności repozytorium, patrz [0004](0004-publiczne-repozytorium.md).

## Źródła

- GitHub Docs, rozliczanie GitHub Actions: standardowe runnery hostowane przez GitHub są bezpłatne w repozytoriach publicznych, https://docs.github.com/en/billing/concepts/product-billing/github-actions (sprawdzone 2026-11-16, `docs/weryfikacja-todo-2026-11-16.md`, G1). Rejestrowane dopiero przy cytowaniu w tekście pracy (`README.md`, zasada 8).
- Łańcuch dostaw w potokach CI/CD: [@NIST-SP800-204D], sek. 3.2.1 (s. 12) i 5.1.2 (s. 18).
