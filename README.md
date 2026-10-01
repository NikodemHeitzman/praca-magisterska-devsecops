# praca-magisterska-devsecops

Repozytorium części praktycznej pracy magisterskiej:

> **Projekt i ewaluacja lekkiego potoku DevSecOps dla aplikacji webowej w chmurze AWS z wykorzystaniem GitHub Actions, Dockera i skanerów bezpieczeństwa zgodnego z wytycznymi OWASP i NIST SP 800-204D**

## Cel

Repozytorium zawiera wszystko, co jest potrzebne do odtworzenia badania:

1. przykładową aplikację webową, którą potok buduje, skanuje i wdraża,
2. infrastrukturę AWS opisaną jako kod (Terraform) i konfigurację hostów (Ansible),
3. dwa potoki GitHub Actions: **bazowy** (build, test, deploy) oraz **DevSecOps** (bazowy oraz skanery SAST, SCA, skanowanie sekretów, obrazów, IaC i DAST),
4. skrypty i dane eksperymentu porównawczego obu potoków (czas wykonania, wykryte podatności, koszt),
5. dokumentację decyzji projektowych (ADR), notatki ze spotkań i dziennik badawczy.

Repozytorium jest publiczne celowo, ponieważ zapewnia bezpłatne GitHub code scanning i nielimitowane minuty GitHub Actions. Nie zawiera żadnych sekretów; dane dostępowe są przechowywane wyłącznie w GitHub Secrets / AWS.

## Struktura

| Katalog | Zawartość |
|---|---|
| `app/` | Aplikacja webowa (obiekt badania) i jej `Dockerfile` |
| `infra/terraform/` | Infrastruktura AWS jako kod |
| `infra/ansible/` | Konfiguracja hostów i wdrożenie |
| `.github/workflows/` | Potoki CI/CD: bazowy i DevSecOps |
| `experiment/` | Skrypty pomiarowe, surowe wyniki, analiza |
| `docs/adr/` | Rejestr decyzji architektonicznych (ADR) |
| `docs/meetings/` | Notatki z konsultacji z promotorem |
| `docs/log/` | Dziennik badawczy |

## Status

Faza F0: organizacja projektu. Struktura katalogów założona, pozostałe elementy w przygotowaniu.

## Ramy odniesienia

- OWASP (m.in. Top 10, ASVS, DevSecOps Guideline)
- NIST SP 800-204D: *Strategies for the Integration of Software Supply Chain Security in DevSecOps CI/CD Pipelines*

## Licencja

TODO: wybrać licencję (np. MIT dla kodu).
