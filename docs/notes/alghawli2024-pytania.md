# Alghawli i Radivilova (2024), klaster chmurowy z DevSecOps: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia kartę pracy w [`literature-matrix.md`](../literature-matrix.md), p. 2.3.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu pracy [@Alghawli2024], 2026-10-14. Przykłady „w naszym projekcie” i oceny oznaczone „ocena agenta” to propozycje agenta, a nie treść pracy.
- Tekst: rękopis autorski z arXiv:2412.16190, plik `Zrodla/pdf/Alghawli2024-arXiv2412.16190.pdf` w vaulcie. Rękopis ma własną numerację („N of 23”), równą numerowi w przeglądarce PDF, więc podaję jeden numer (s. N). Wersja w *Alexandria Engineering Journal* ma s. 136–149 i inny układ. Przed cytowaniem strony sprawdź ją w wersji wydawcy, która jest w otwartym dostępie.
- Treść zajmuje s. 1–20, dalej jest bibliografia.

---

## Najpierw w pięciu zdaniach

1. Autorzy **budują w AWS klaster dla aplikacji webowej** z Terraform, Dockerem i potokiem Jenkins, w którym SonarQube skanuje kod.
2. Dodają **własny algorytm ilościowej oceny ryzyka** oparty na triadzie CIA (poufność, integralność, dostępność) i metodyce FAIR.
3. **AWS wybierają metodą AHP Saaty’ego** spośród AWS, Azure i GCP. Waga AWS wyniosła 50,9%, ale ocenę przeprowadzili sami autorzy według własnych założeń.
4. Dają **praktyczne zalecenia dla usług AWS**: szyfrowanie, prywatna podsieć dla bazy, WAF, GuardDuty, stan Terraform w S3.
5. W mojej pracy to **najbliższa praca pokrewna technologicznie** (2.3, 4.2). Jest też kontrastem, bo ma jeden skaner, nie mierzy skuteczności ani kosztu, a jej wyniki są nieodtwarzalne.

---

## 1. Problem i cel (rozdz. 1–2; s. 1–4)

**Jaki problem badają autorzy?**

Presja terminów sprawia, że w projektach chmurowych zaniedbuje się bezpieczeństwo (s. 1). Istniejące podejścia osobno automatyzują wytwarzanie, osobno liczą podatności w kodzie i osobno ryzyko organizacji. Autorzy chcą połączyć te trzy zadania (s. 2).

**Jaki jest cel pracy?** (s. 2)

Zbudować klaster w chmurze z automatycznym obliczaniem podatności i ilościową oceną ryzyka przy bezpiecznym wytwarzaniu oprogramowania.

**Jaką lukę wskazują w literaturze?** (s. 4)

Metody oceny ryzyka w chmurze są albo niezautomatyzowane, albo nieilościowe, albo pomijają podatności związane z wytwarzaniem oprogramowania, albo dotyczą jednego dostawcy.

---

## 2. Algorytm oceny ryzyka (rozdz. 4; s. 6–9)

**Jakie są kroki algorytmu?** (s. 6)

1. Baza komponentów systemu.
2. Baza zdarzeń.
3. Analiza wpływu zagrożeń na CIA, na początek ekspercka.
4. Modelowanie zagrożeń i podatności.
5. Obliczenie wpływu.
6. Obliczenie prawdopodobieństwa.
7. Obliczenie ryzyka.
8. Wdrożenie środków kontroli i ponowne obliczenie ryzyka.

Algorytm uruchamia się ponownie przy każdej zmianie systemu (s. 6–7).

**Czym jest FAIR i co autorzy w nim zmieniają?** (s. 7–8)

FAIR (Factor Analysis of Information Risk) szacuje ryzyko z częstości incydentów i prawdopodobnych strat, ale wynik ma postać przedziałów jakościowych. Autorzy przechodzą na wartość ilościową:
- prawdopodobieństwo naruszenia każdej składowej CIA liczą ze wzoru na co najmniej jedno z niezależnych zdarzeń (wzór 1) i ze wzoru na prawdopodobieństwo całkowite (wzór 2),
- ryzyko to suma iloczynów prawdopodobieństw i strat (wzór 3) (s. 8–9).

**Jak sprawdzili ten algorytm?** (s. 9, 18)

Piszą, że wynik „mieścił się w przedziale” wyznaczonym metodą standardową (s. 9), ale nie podają liczb. W eksperymencie na klastrze (Tabela 4, s. 18) wyszły:
- prawdopodobieństwa naruszeń 0,77, 0,68 i 0,81,
- ryzyko 4184,6, 3819,3 i 4475,5 jednostek umownych.

**Co jest słabe w tym wyniku?** (ocena agenta)

Brak danych wejściowych: jakie zdarzenia, hipotezy, prawdopodobieństwa cząstkowe i kwoty strat. Nie da się więc odtworzyć wyniku ani ocenić, czy jest sensowny. *W naszym projekcie:* dlatego zapisujemy surowe dane eksperymentu, a nie tylko wyniki końcowe (zasada odtwarzalności z `AGENTS.md`).

---

## 3. Wybór dostawcy chmury (rozdz. 5.1; s. 9–13)

**Jak wybierali dostawcę?** (s. 9–12)

Metodą AHP (analityczny proces hierarchiczny) Saaty’ego: porównania parami w skali 1–9, normalizacja macierzy i średnie z wierszy dają wagi kryteriów, a potem wagi dostawców.

**Jakie były kryteria i dane?** (s. 10–11, Tabela 1)

| Kryterium | AWS | Azure | GCP |
|---|---|---|---|
| Koszt ruchu (za GB) | 0,085 | 0,0875 | 0,11 |
| Liczba regionów (2023) | 25 | 60 | 24 |
| Koszt klastra (mies.) | 350,37 USD | 513,89 USD | 365,21 USD |
| Liczba usług bezpieczeństwa | 33 | 30 | 26 |
| Czas wdrożenia przez Terraform | 6,3 min | 6,5 min | 7 min |

Czas wdrożenia zmierzono w eksperymencie trwającym 10 kolejnych dni, z Terraform v0.12, w regionie Niemcy (s. 10).

**Co wyszło?** (Tabela 2 s. 12, Tabela 3 s. 12)

- Najważniejsze kryteria: liczba usług bezpieczeństwa (52,1%) i koszt klastra (24,8%).
- Wagi dostawców: AWS 50,9%, Azure 33,6%, GCP 15,5%.

**Na co uważać, cytując ten wybór?** (s. 13, ocena agenta)

Autorzy sami piszą, że analiza była ekspercka i oparta na wymaganiach, które sami przyjęli (s. 13). To nie jest dowód, że AWS jest obiektywnie najlepszy. W tym samym fragmencie jest błąd rzeczowy: Kubernetes i Azure nazwano projektami Google (s. 13), a Azure to usługa Microsoft.

*W naszym projekcie:* wybór AWS uzasadnia ADR według powodów autora pracy magisterskiej. Ta praca może być najwyżej przykładem, że w literaturze też wybierano AWS, a nie argumentem rozstrzygającym.

---

## 4. Architektura w AWS (rozdz. 5.2; s. 13–18)

**Jakie zalecenia dają dla usług AWS?** (s. 14–17)

- **Terraform:** stan (`terraform.tfstate`) trzymać w S3, nie lokalnie (s. 14).
- **EC2:** szyfrowane dyski EBS, klucze SSH RSA o długości co najmniej 2048 bitów, SSH v2, zmiana portu SSH (s. 15).
- **ECR:** tylko prywatne obrazy, dostęp dla wybranych osób i systemów CI/CD (s. 16).
- **ECS:** grupa autoskalowania, min. 2, maks. 4 (s. 16).
- **VPC:** co najmniej 2 strefy dostępności, prywatna podsieć dla bazy danych (s. 16).
- **Security Groups:** osobne dla serwerów, bazy i load balancera, tylko potrzebne porty (s. 16).
- **RDS:** prywatna podsieć, szyfrowanie, multi-AZ (s. 16).
- **Load balancer:** własny certyfikat, tylko TLS 1.2 i 1.3, porty 80 i 443 (s. 16).
- **S3:** szyfrowanie obiektów, osobny użytkownik IAM tylko do S3 (s. 16).
- **CloudWatch, SNS, GuardDuty:** logi, alerty i reagowanie na zgłoszenia o średnim i wysokim poziomie (s. 16–17).
- **WAF:** reguły blokujące XSS, SQLi i nadmiar żądań, 3000 na godzinę (s. 16–17).

*W naszym projekcie:* część tych zaleceń warto porównać z naszą infrastrukturą w 4.2, np. stan w S3, szyfrowanie, prywatna podsieć. Checkov i Trivy sprawdzają wiele z nich automatycznie.

**Które zalecenia są wątpliwe?** (ocena agenta)

- Użytkownik IAM z **prawami administratora i dostępem programowym** dla Terraform oraz przykład polityki `AmazonS3FullAccess` (s. 17). To narusza zasadę najmniejszych uprawnień i oznacza długoterminowe klucze. *W naszym projekcie:* OIDC z GitHub Actions i role z minimalnymi uprawnieniami.
- **Zmiana portu SSH** jako środek bezpieczeństwa (s. 15) to ukrywanie, a nie zabezpieczenie. Do tego jest niespójność: port 37337 na s. 15 i 37377 na s. 17.

---

## 5. Potok CI/CD (rozdz. 5.2; s. 18)

**Jak wygląda ich potok?** (s. 18)

1. Push do GitHub.
2. Jenkins wykrywa commit przez webhook.
3. SonarQube skanuje kod, a algorytm liczy ryzyko CIA.
4. Jeśli wynik jest pozytywny, powstaje obraz Docker, trafia do ECR, a wdrożenie blue-green wykonuje AWS CodePipeline.

**Czego w nim brakuje w porównaniu z moim potokiem?** (ocena agenta)

- Jest tylko **jeden skaner**, SonarQube (SAST). Brakuje analizy zależności (SCA), skanowania obrazu kontenera, IaC i sekretów.
- **Nie ma pomiaru**: ile podatności wykryto, ile zatrzymano, ile trwa skan, ile jest fałszywych alarmów.
- **Nie ma łańcucha dostaw**: SBOM, podpisów, atestacji, SLSA. W tekście nie ma też OWASP, a NIST pojawia się tylko w bibliografii, przy NIST CSF i FAIR.

---

## 6. Pytania, które może zadać recenzent

**„Czym Twoja praca różni się od Alghawli i Radivilovej, skoro też robicie DevSecOps w AWS z Terraform?”**

Oni projektują infrastrukturę i model ryzyka, a potok ma jeden skaner i nie jest oceniany. Ja porównuję dwa warianty potoku i mierzę, ile podatności dociera na produkcję (RQ1) i ile to kosztuje (RQ2). Oceniam też zgodność z SP 800-204D i OWASP (RQ3). Zapisuję surowe dane, więc wynik można odtworzyć.

**„Dlaczego nie liczysz ryzyka jak oni?”**

Ich wyniki ryzyka nie mają danych wejściowych, więc nie da się ich sprawdzić. Moje pytania dotyczą skuteczności i kosztu potoku, a nie wyceny ryzyka organizacji.

**„Czy ta praca uzasadnia wybór AWS?”**

Tylko częściowo. Autorzy sami nazywają swoją analizę ekspercką, opartą na własnych założeniach (s. 13). Wybór AWS w mojej pracy uzasadnia osobny ADR.
