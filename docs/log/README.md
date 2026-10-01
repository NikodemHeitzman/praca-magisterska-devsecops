# Dziennik badawczy

Datowane wpisy z przebiegu pracy: co zrobiono, jakie zapadły decyzje, jakie były problemy i ile czasu to zajęło. Dziennik jest źródłem materiału do rozdziału 4 (przebieg realizacji, środowisko badawcze) i do podrozdziału 5.3 (ograniczenia).

## Zasady

1. **Jeden plik na dzień:** `RRRR-MM-DD.md`. Kolejna sesja tego samego dnia dopisuje sekcję `## Sesja N` w tym samym pliku.
2. **Wpis na koniec każdej sesji pracy**, także sesji agenta AI. Wystarczą 3 minuty. Kopiuj [`_szablon.md`](_szablon.md).
3. **Czas pracy** podawaj w godzinach z dokładnością do 0,25 h. Jeśli go nie znasz, wpisz `TODO: zweryfikować`. Nie szacuj w ciemno, bo czasy trafią do analizy kosztu wdrożenia potoku.
4. **Decyzje** zapisuj tu krótko. Wybór techniczny dostaje dodatkowo ADR w [`../adr/`](../adr/), a we wpisie link do niego.
5. **Problemy** opisuj z objawem i obejściem. Nierozwiązane zostają na liście otwartych kwestii, dopóki ich nie zamkniesz w późniejszym wpisie.
6. **Repozytorium jest publiczne.** Nie wpisuj sekretów, identyfikatorów kont AWS, adresów e-mail ani treści prywatnych rozmów.

## Dla agentów AI

Każdy agent (Claude Code, Copilot, Codex i inne), który kończy sesję pracy w tym repozytorium albo nad pracą magisterską, dopisuje wpis do pliku z bieżącą datą. W polu „Autor” podaje nazwę narzędzia. Zasada jest też w [`AGENTS.md`](../../AGENTS.md).

## Związek z vaultem Obsidiana

Vault `Magisterka-Vault` ma własny `Dziennik/RRRR-MM-DD.md`. Trafia tam tylko lista zadań zamkniętych na tablicy (`/task-done`), z linkami do notatek zadań. Ten dziennik jest pełniejszy: obejmuje czas, decyzje, problemy i pracę, która nie zamyka żadnego zadania. W razie rozbieżności co do przebiegu pracy rozstrzyga ten dziennik, a co do statusów zadań tablica.
