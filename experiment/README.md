# Eksperyment

Katalog `experiment/` zawiera dane i skrypty eksperymentu porównawczego wariantu A (CI/CD bez kontroli bezpieczeństwa) i wariantu B (potok DevSecOps). Założenia badania są w [`docs/metodyka.md`](../docs/metodyka.md).

| Plik | Zawartość | Zadanie |
|---|---|---|
| [`ground-truth.yaml`](ground-truth.yaml) | katalog podatności referencyjnych (ground truth) | E03-03 |
| [`scripts/validate_ground_truth.py`](scripts/validate_ground_truth.py) | walidacja katalogu i kryteriów | E03-03 |
| `PROTOCOL.md` | procedura eksperymentu | E03-05 (do zrobienia) |
| `data/` | surowe wyniki przebiegów | E09 (do zrobienia) |

## Katalog podatności referencyjnych

### Po co

Katalog to znana „prawda”: lista podatności celowo wprowadzonych do aplikacji, jej kontenera, infrastruktury i workflow. Bez niego nie dałoby się policzyć skuteczności potoku, bo nie wiadomo by było, ile podatności powinien znaleźć. Na katalogu opierają się metryki M1–M3 i hipoteza H1 (`docs/metodyka.md`, p. 2.2–2.3).

Wersja czysta aplikacji (gałąź `main`) nie zawiera żadnej pozycji z katalogu. Każda pozycja trafia do eksperymentu jako osobny pull request oznaczony identyfikatorem, np. `seed/GT-01` (E04-04).

### Skład (v0, 2026-10-09)

20 pozycji w 6 grupach, w tym 3 celowo poza zasięgiem narzędzi. Pozycje obejmują wszystkie 10 kategorii OWASP Top 10:2025.

| Grupa | Pozycje |
|---|---|
| kod | GT-01 SQL injection, GT-02 zakodowany sekret JWT, GT-03 MD5 dla haseł, GT-04 `eval`, GT-05 path traversal, GT-06 log injection |
| zależności | GT-07 Jinja2 3.1.2 (znane CVE) |
| kontener | GT-08 nieutrzymywany obraz bazowy, GT-09 uruchamianie jako root |
| IaC | GT-10 port 22 otwarty dla 0.0.0.0/0, GT-11 nieszyfrowany magazyn danych |
| konfiguracja web | GT-12 CORS `*`, GT-13 brak ochrony przed clickjackingiem, GT-14 debug ze stack trace |
| workflow | GT-15 `permissions: write-all`, GT-16 akcja niepinowana do SHA, GT-17 wstrzyknięcie skryptu przez kontekst zdarzenia |
| kod, poza zasięgiem narzędzi | GT-18 IDOR, GT-19 brak autoryzacji funkcji administratora, GT-20 mass assignment roli |

Decyzje autora z 2026-10-09: 20 pozycji, w tym 3 poza zasięgiem narzędzi (15%); CWE-250 dla uruchamiania kontenera jako root bez kategorii Top 10.

**Pozycje rezerwowe** (rozważone, poza v0): deserializacja `pickle` (CWE-502), IMDSv1 (CWE-1188; zależy od użycia EC2 w E05), wstrzyknięcie poleceń systemu (CWE-78 w aplikacji), SSRF (CWE-918), słaby generator losowy (CWE-338), katalog `.git` w obrazie, druga zależność z CVE. Mogą zastąpić pozycję, która okaże się niewykonalna w E04/E05. Każdą zamianę zapisujemy w dzienniku.

### Pola pozycji

| Pole | Znaczenie |
|---|---|
| `id` | stały identyfikator `GT-NN`, używany w nazwie gałęzi i PR |
| `grupa` | `kod`, `zaleznosci`, `kontener`, `iac`, `konfiguracja-web`, `workflow` |
| `cwe` | najbardziej precyzyjne CWE, które MITRE dopuszcza do mapowania (status *Allowed* albo *Allowed-with-Review*) |
| `owasp_top10_2025` | kategoria Top 10:2025, **tylko** gdy CWE jest na liście CWE tej kategorii; w przeciwnym razie `null` |
| `owasp_cicd` | ryzyko z OWASP Top 10 CI/CD dla pozycji potoku i łańcucha dostaw; wstępnie, do weryfikacji w E02-04 |
| `asvs` | wymaganie ASVS 5.0.0 łamane przez pozycję (`null`, gdy ASVS nie obejmuje, np. Terraform, workflow) |
| `lokalizacja` | plik albo zasób, po którym rozpoznajemy trafienie |
| `wprowadzenie` | co zmienia pull request względem wersji czystej |
| `referencje` | identyfikatory podatności i obrazów sprawdzone w źródle (OSV, Docker Hub), z datą |
| `w_zasiegu_narzedzi` | `false` = żadna klasa narzędzi w potoku nie jest zaprojektowana do wykrycia tej podatności |
| `pewnosc_detekcji` | hipoteza autora przed eksperymentem: `wysoka`, `srednia`, `niska`, `brak` |
| `oczekiwany_detektor` | klasa narzędzia i kandydat z listy E02-10; konkretne reguły ustali E02-10/E07 |
| `najwczesniejszy_etap` | najwcześniejszy etap, na którym może zadziałać detektor danej klasy: `PR`, `main-przed-wdrozeniem`, `po-uruchomieniu`, `brak` |

Oczekiwany detektor i etap to **hipotezy zapisane przed eksperymentem**. Wynik eksperymentu może je potwierdzić albo obalić; rozbieżności są wynikiem, a nie błędem katalogu.

### Zasady klasyfikacji

1. **CWE.** Nazwę i status mapowania sprawdzamy w bazie MITRE (cwe-api.mitre.org). Nie używamy CWE oznaczonych przez MITRE jako *Discouraged* (np. CWE-284, CWE-311, CWE-693), tylko ich bardziej precyzyjnych potomków.
2. **Kategoria Top 10:2025** wynika wyłącznie z list CWE kategorii (`docs/notes/owasp-asvs-samm.md`, p. 6). ASVS 5.0 nie mapuje wymagań na CWE, więc nie jest źródłem CWE.
3. **Numery CVE i obrazy** bierzemy z OSV, NVD albo Docker Hub, z datą sprawdzenia. Nie z pamięci (`AGENTS.md`, zasada 7).
4. **Sekrety w katalogu są fikcyjne.** Repozytorium jest publiczne.

### Jak liczymy trafienia (dla M1–M3)

- **Trafienie** to zgłoszenie narzędzia, które wskazuje lokalizację pozycji (plik, zasób, pakiet albo obraz) i dotyczy tej samej słabości. Zgodność oceniamy ręcznie według opisu pozycji, a nie tylko po numerze CWE, bo narzędzia przypisują CWE różnie.
- Dla GT-07 trafieniem jest zgłoszenie dowolnej podatności z listy `referencje` dla `jinja2`. Dla GT-08: zgłoszenie systemu po końcu wsparcia albo podatności w pakietach systemowych obrazu bazowego.
- Zgłoszenia, które nie są trafieniem żadnej pozycji, klasyfikujemy jako prawdziwy problem spoza katalogu albo fałszywy alarm (H2b, M6). Dotyczy to też nowych CVE, które pojawią się w zależnościach wersji czystej w trakcie eksperymentu.
- **M1 (wykrywalność)** = liczba pozycji z co najmniej jednym trafieniem / 20, ogółem i w każdej grupie.
- **M2 (etap wykrycia)** = najwcześniejszy etap, na którym pojawiło się trafienie.
- **M3 (dotarło na produkcję)** = pozycje, których żadna bramka blokująca nie zatrzymała przed wdrożeniem / 20, w każdym wariancie. Potwierdzamy je audytem środowiska po wdrożeniu ([`PROTOCOL.md`](PROTOCOL.md), sekcja 4). Klasy wyniku próby, w tym zasada, że blokada bez trafienia pozycji nie jest zatrzymaniem: [`PROTOCOL.md`](PROTOCOL.md), p. 3.3.

### Pułap H1

H1 wymaga, żeby wariant B zatrzymał co najmniej 80% pozycji. Skład katalogu wyznacza pułap tego wyniku: przy trzech pozycjach poza zasięgiem narzędzi wariant B może zatrzymać najwyżej **17/20 = 85%**.

Miejsce DAST rozstrzygnięto w E03-05 (decyzja autora z 2026-10-13): OWASP ZAP w trybie baseline jest w wariancie B bramką na każdym pull requeście, na kontenerze uruchomionym w runnerze ([`PROTOCOL.md`](PROTOCOL.md), sekcja 0). Pozycje wykrywane tylko przez DAST (GT-13, a bez reguł SAST także GT-12 i GT-14) mogą więc zostać zatrzymane przed wdrożeniem, a pułap pozostaje na 85%. Odrzucone warianty z 2026-10-09 dawały pułap 80% albo 70% (DAST tylko po wdrożeniu).

Pułap może się obniżyć, jeśli ZAP w trybie pasywnym nie wykryje którejś z pozycji GT-12–14 (zwłaszcza GT-14, która wymaga wywołania błędu serwera), a SAST nie ma dla niej reguły. TODO: zweryfikować w E02-10.

Skład katalogu ustalono 2026-10-09, **przed** decyzją o miejscu DAST, i nie dopasowujemy go do progu H1, żeby nie dobierać podatności pod narzędzia (zagrożenie trafności wewnętrznej TW1, `docs/metodyka.md`, p. 4.5).

### Bezpieczeństwo eksperymentu

Część pozycji to podatności możliwe do realnego wykorzystania (np. GT-04 `eval` pozwala wykonać kod, GT-17 dotyczy workflow w publicznym repozytorium). Wariant A wdraża je do AWS. Wymagania dla scenariusza i infrastruktury (E05), potwierdzone przez autora 2026-10-13 i rozwinięte w [`PROTOCOL.md`](PROTOCOL.md), sekcja 6:

- środowisko eksperymentu jest krótkotrwałe i nie zawiera prawdziwych danych,
- dostęp do aplikacji na czas eksperymentu ograniczony do znanych adresów (lista dozwolonych adresów IP), o ile nie przeszkadza to w audycie,
- przy GT-10 instancja nie ma klucza SSH ani logowania hasłem, więc otwarty port nie daje dostępu,
- workflow nie używa `pull_request_target`, a pull requesty eksperymentu pochodzą wyłącznie z gałęzi własnego repozytorium; workflow z GT-17 nie ma dostępu do sekretów,
- sekrety w katalogu (GT-02) są fikcyjne.

### Walidacja

```bash
python experiment/scripts/validate_ground_truth.py
```

Skrypt sprawdza schemat pozycji i kryteria katalogu (min. 15 pozycji w min. 5 grupach, CWE i detektor przy każdej pozycji, pozycje poza zasięgiem) oraz wypisuje pokrycie kategorii Top 10 i pułap H1. Wymaga PyYAML.

### Wersjonowanie

Katalog ma wersję `v0` do akceptacji metodyki przez promotora (E03-07). Potem zostaje zamrożony jako `v1`. Każdą późniejszą zmianę (zamiana pozycji, zmiana `w_zasiegu_narzedzi` po wyborze reguł w E02-10) zapisujemy w dzienniku badawczym z uzasadnieniem, przed uruchomieniem eksperymentu.
