# Ustawienia platformy GitHub

Spis ustawień repozytorium, które należą do potoku, ale nie są w plikach workflow (CICD-SEC-7 [@OWASP-Top10-CICD]). Decyzje i powody autora są w [ADR-0043](adr/0043-utwardzenie-workflowow.md), a kroki potoku w [`projekt-potoku.md`](projekt-potoku.md), sekcja 3.

Źródłem prawdy są pliki w [`infra/github/`](../infra/github/): rulesety jako JSON w `rulesets/`, pozostałe ustawienia w skrypcie `settings.sh`. Ten dokument je opisuje, ale ich nie zastępuje.

## Jak używać

Lokalnie, w Git Bash, z katalogu repozytorium, zalogowany przez `gh` jako właściciel repozytorium:

```bash
infra/github/settings.sh show    # odczyt obecnego stanu, nic nie zmienia
infra/github/settings.sh apply   # zastosowanie ustawień i rulesetów z repozytorium
```

Zmiana ustawienia: najpierw zmiana pliku w `infra/github/` w PR, po scaleniu `apply`. Wynik `show` po `apply` porównujemy z plikami. Rozbieżność oznacza zmianę ręczną w interfejsie (dryf).

## Spis

| Ustawienie | Wartość docelowa | Przed E07-02 (2026-11-23) | Gdzie zapisane | Krok | Decyzja |
|---|---|---|---|---|---|
| Ruleset `main` | PR wymagany (0 zatwierdzeń), wymagane checki `lint`, `test`, `build`, `workflow-lint` z GitHub Actions, blokada force push i usunięcia, bez obejść | brak | `rulesets/main.json` | B02 | H1–H3, H11 |
| Ruleset `exp-variant-b` | jak `main`, a do tego obejście dla roli admina (`always`) i `do_not_enforce_on_create` | brak | `rulesets/variant-b.json` | B02 | H1, H3, H13 |
| Ruleset `tags` | wszystkie tagi: zakaz usunięcia, force push i przesunięcia | brak | `rulesets/tags.json` | (odtwarzalność) | H11 |
| Secret scanning i push protection | włączone | włączone | `settings.sh` | B03 | ADR-0042 |
| Dependabot: alerty | włączone | wyłączone | `settings.sh` | B04 | H6 |
| Dependabot: security updates | włączone | wyłączone | `settings.sh` | B04 | H6 |
| Dependabot: aktualizacje wersji | `github-actions`, `uv`, `docker`, co tydzień, karencja 7 dni | brak pliku | `.github/dependabot.yml` | B04 | H6 |
| Domyślne uprawnienia `GITHUB_TOKEN` | tylko odczyt, bez zatwierdzania PR | tak samo | `settings.sh` | B05 | ADR-0042 |
| Zgoda na workflow z forków | wszyscy zewnętrzni kontrybutorzy | tylko pierwszy wkład | `settings.sh` | B05 | H9 |
| Dozwolone akcje | akcje GitHuba i lista `allowed_patterns` (`astral-sh/setup-uv@*`) | wszystkie | `settings.sh` | B05 | H7 |
| Wymuszenie przypinania do SHA | włączone | wyłączone | `settings.sh` | B05 | H7 |
| Właściciele kodu | autor dla całego repozytorium; przegląd niewymagany | brak | `.github/CODEOWNERS` | B02 | H5 |
| Lint workflowów | actionlint i zizmor (`regular`, od `low`) na PR i pushu | tylko lokalnie | `.github/workflows/workflow-lint.yml` | B16, B17 | H8, H10, D5 |

Zawartość wymaganych checków rośnie z zadaniami E07-03…E07-10 (H3). Każde z nich dopisuje nazwę swojego joba w obu plikach rulesetów gałęzi.

## Czego platforma nie pokrywa

- Drugiego recenzenta: przy jednym autorze PR nie ma niezależnego przeglądu, a CODEOWNERS jest tylko śladem (H5).
- Podpisanych commitów i kontroli ruchu wychodzącego z runnera (D11, H4).
- Ustawień konta autora (2FA, klucze, tokeny), które chronią wszystkie powyższe. TODO: zweryfikować i opisać w 5.3 jako założenie.
