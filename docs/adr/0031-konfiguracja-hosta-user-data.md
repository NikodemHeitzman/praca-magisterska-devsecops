# 0031. Konfiguracja i utwardzenie instancji: skrypt user-data zamiast Ansible

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0024](0024-architektura-aws-ec2-docker-compose.md), [0028](0028-system-instancji-ubuntu-przypiete-ami.md), [0019](0019-srodowisko-efemeryczne-aws.md), [0022](0022-obraz-kontenera-aplikacji.md), zadania E05-05, E05-07, [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Instancja EC2 z E05-04 startuje z gołego obrazu Ubuntu 24.04 (ADR-0028). Do uruchomienia stosu potrzebuje Dockera z wtyczką compose. Za system operacyjny odpowiada autor (model współdzielonej odpowiedzialności, ADR-0024), więc host trzeba też utwardzić. Ograniczenia:

- dostęp tylko przez SSM, bez klucza SSH i bez portu 22 (ADR-0024),
- środowisko jest efemeryczne: instancja powstaje od zera przy każdym `apply` (ADR-0019),
- autor pracuje na Windows,
- zadanie jest w katalogu oznaczone jako opcjonalne, a czas jest potrzebny na potoki i eksperyment.

Katalog zadań proponował Ansible, a jako alternatywę user-data w Terraformie, z decyzją opisaną w ADR.

## Czynniki decyzyjne

- sposób dostępu do hosta (SSM bez SSH) i system operacyjny stacji autora,
- czas realizacji,
- liczba narzędzi w lekkim potoku,
- prostota utrzymania i aktualizacji,
- zgodność z wcześniejszymi decyzjami (ADR-0024, ADR-0028).

## Rozważane opcje

Mechanizm konfiguracji:

1. skrypt user-data wykonywany przez cloud-init przy pierwszym starcie
2. playbook Ansible uruchamiany po `apply` przez wtyczkę połączenia SSM
3. oba: user-data instaluje Dockera, Ansible utwardza

Źródło Dockera:

1. pakiety `docker.io` i `docker-compose-v2` z archiwum Ubuntu
2. pakiety `docker-ce` i `docker-compose-plugin` z repozytorium Dockera

Serwer SSH:

1. wyłączony i zablokowany
2. włączony, z utwardzoną konfiguracją (bez logowania roota i haseł)
3. bez zmian

Zapora na hoście:

1. tylko grupa bezpieczeństwa
2. grupa bezpieczeństwa i ufw

Aktualizacje:

1. automatyczne łatki bezpieczeństwa, bez pełnego `apt upgrade` przy starcie
2. pełny `apt upgrade` przy starcie i automatyczne łatki
3. bez automatycznych aktualizacji

Użytkownik uruchamiający stos:

1. dedykowany użytkownik `app` w grupie `docker`
2. Docker w trybie rootless
3. bez użytkownika serwisowego (root przez SSM)

## Decyzja

Wybrano **skrypt user-data (bash) w Terraformie, Dockera z archiwum Ubuntu, wyłączony serwer SSH, tylko grupę bezpieczeństwa jako zaporę, automatyczne łatki bezpieczeństwa bez pełnego upgrade'u przy starcie i dedykowanego użytkownika `app` w grupie `docker`.** Wszystkie wybory były rekomendacją agenta. Autor je przyjął i wskazał powody z listy przygotowanej przez agenta. Powody autora:

- **User-data zamiast Ansible:**
  - brak SSH i Windows: Ansible nie działa na Windows jako węzeł sterujący bez WSL (dokumentacja Ansible), a bez SSH musiałby łączyć się wtyczką `aws_ssm`, która wymaga kubełka S3 do przesyłania plików, nawet dla modułów `shell` i `command`, oraz wtyczki Session Manager na stacji sterującej (dokumentacja `amazon.aws.aws_ssm`),
  - czas,
  - mniej narzędzi w lekkim potoku.
- **Docker z archiwum Ubuntu zamiast repozytorium Dockera:**
  - aktualizacje bezpieczeństwa Dockera przychodzą razem z systemem,
  - prostota.
- **Wyłączony serwer SSH zamiast utwardzonego:**
  - mniejsza powierzchnia ataku,
  - spójność z ADR-0024 (dostęp tylko przez SSM).
- **Tylko grupa bezpieczeństwa, bez ufw:**
  - Docker omija ufw: ruch do opublikowanych portów kontenerów jest przekierowywany w tablicy `nat`, zanim zadziałają reguły ufw (dokumentacja Dockera, *Packet filtering and firewalls*), więc ufw dawałby fałszywe poczucie ochrony,
  - prostota.
- **Automatyczne łatki bezpieczeństwa bez pełnego upgrade'u:**
  - czas startu środowiska,
  - `unattended-upgrades` jest w Ubuntu włączony domyślnie, a skrypt tylko jawnie to potwierdza. Potwierdzono na instancji (sekcja „Weryfikacja”); dokumentacja Ubuntu była 2026-11-11 niedostępna (TODO: zweryfikować w dokumentacji).
- **Użytkownik `app` w grupie `docker` zamiast trybu rootless:**
  - tryb rootless komplikuje port 80 i dostęp kontenera do IMDS,
  - izolację zapewnia kontener: aplikacja działa w nim jako użytkownik bez uprawnień roota (ADR-0022),
  - czas.

- **Wersje Dockera bez przypinania, jako świadome odstępstwo od zasady 6 `AGENTS.md`** (decyzja po teście):
  - łatki bezpieczeństwa: host z publicznym IP powinien dostawać poprawki Dockera, a przypięcie by je blokowało,
  - przypięcie się psuje: Ubuntu usuwa starsze wersje z `-updates`, więc instalacja przypiętej wersji po pewnym czasie przestałaby działać,
  - wersje i tak są zapisane: `check-host.sh` wypisuje je dla każdego przebiegu,
  - Docker nie jest obiektem pomiaru: eksperyment porównuje potoki, a nie wersje Dockera na hoście.

Kryterium „playbook idempotentny” z katalogu zadań przeniesiono na skrypt: każdy krok sprawdza stan przed zmianą, a drugie uruchomienie przez SSM musi zgłosić zero zmian.

Decyzje agenta, przyjęte bez osobnego pytania:

- skrypt bash zamiast dyrektyw `#cloud-config`, bo da się go uruchomić ponownie przez SSM i zmierzyć liczbę zmian,
- `user_data_replace_on_change = true`: zmiana skryptu tworzy nową instancję, więc host nie dryfuje względem kodu,
- `/etc/docker/daemon.json`: rotacja logów kontenerów (`json-file`, 3 × 10 MB, żeby logi nie zapełniły dysku 20 GiB) i `no-new-privileges` dla wszystkich kontenerów,
- `ssh.socket` i `ssh.service` zamaskowane, bo w Ubuntu 24.04 sshd startuje przez aktywację gniazdem (na instancji `ssh.socket` był włączony; sekcja „Weryfikacja”),
- `Unattended-Upgrade::Automatic-Reboot "false"` jawnie, bo host jest efemeryczny,
- czekanie na blokadę dpkg (`DPkg::Lock::Timeout`), bo zaraz po starcie może ją trzymać `apt-daily`.

## Weryfikacja

Test 2026-11-11 w `eu-north-1`, instancja `t3.small` z przypiętym AMI, kontrola skryptem [`check-host.sh`](../../infra/terraform/check-host.sh) przez SSM Run Command z CloudShell. Pojedynczy pomiar:

- **Pierwsze przebiegnięcie** (cloud-init): 7 zmian. Instalacja `docker.io` i `docker-compose-v2`, `daemon.json`, utworzenie użytkownika `app` i dodanie go do grupy `docker`, maskowanie `ssh.socket` i `ssh.service`, plik `52devsecops-unattended-upgrades`. Moduł `scripts_user` trwał 25,3 s, cały cloud-init 28,7 s.
- **Drugie przebiegnięcie** przez SSM: `harden: done, 0 change(s)` w czasie poniżej 1 s. Kryterium idempotencji jest spełnione.
- **Wartości domyślne obrazu:**
  - `unattended-upgrades` był zainstalowany, a `20auto-upgrades` miał już tę samą treść co skrypt (skrypt go nie zmienił),
  - ufw był nieaktywny,
  - `ssh.socket` istniał i nie był zamaskowany.
- **Wersje z archiwum Ubuntu** (z `noble-updates`):
  - `docker.io` 29.1.3-0ubuntu3~24.04.2,
  - `docker-compose-v2` 2.40.3+ds1-0ubuntu1~24.04.1,
  - `containerd` 2.2.1-0ubuntu1~24.04.4,
  - `runc` 1.3.4-0ubuntu1~24.04.1,
  - `unattended-upgrades` 2.9.1+nmu4ubuntu1.
- **Źródła łatek** (`apt-config dump`): `${distro_codename}`, `-security`, ESM Apps i ESM Infra, bez `-updates`; `Automatic-Reboot "false"`. Pakiety z `noble-updates` nie są więc instalowane automatycznie, tylko przy instalacji przez skrypt.
- **Stan po utwardzeniu:**
  - `ssh.socket` i `ssh.service` są `masked / inactive`, nic nie nasłuchuje na porcie 22,
  - nasłuchują tylko `systemd-resolved` (127.0.0.53 i 127.0.0.54, port 53) i `containerd` (127.0.0.1),
  - agent SSM (snap) jest `enabled / active`,
  - `docker` jest `enabled / active`.
- **Użytkownik `app`:** UID 999, powłoka `/usr/sbin/nologin`, grupy `app` i `docker`, `/opt/app` z właścicielem `app:app` i prawami 750.

## Konsekwencje

- (+) Utwardzenie dzieje się samo przy każdym `apply`. Nie ma kroku, o którym można zapomnieć, ani narzędzia do przypięcia i opisania.
- (+) Skrypt jest w repozytorium obok Terraformu, więc skanery IaC i przegląd kodu widzą go razem z instancją.
- (−) User-data działa tylko przy pierwszym starcie (dokumentacja EC2). Zmiana konfiguracji działającego hosta wymaga nowej instancji albo ręcznego uruchomienia skryptu przez SSM. Przy środowisku efemerycznym to akceptowalne.
- (−) Limit user-data to 16 KB (dokumentacja EC2). Skrypt ma około 4 KB.
- (−) Członkostwo w grupie `docker` daje uprawnienia na poziomie roota (dokumentacja Dockera, *Linux post-installation steps*). Użytkownik `app` nie ma powłoki logowania, ale kto przejmie to konto, przejmie host. Materiał do 5.3.
- (−) Wersje Dockera z archiwum Ubuntu są starsze od wydań Dockera (ADR-0028), choć z `noble-updates` przychodzą nowsze niż w wydaniu bazowym (sekcja „Weryfikacja”). Wersje zależą od dnia `apply`, bo skrypt instaluje to, co jest wtedy w archiwum. Nie są przypięte (świadome odstępstwo, sekcja „Decyzja”), więc wersje każdego przebiegu eksperymentu trzeba zapisać razem z jego danymi (`check-host.sh` albo krok wdrożenia, E05-07 i E09).
- (−) Instancja nie dostaje pełnego `apt upgrade` przy starcie. Łatki bezpieczeństwa przychodzą z `unattended-upgrades` według harmonogramu, a nie od razu, więc świeży host przez pewien czas może mieć znane podatności z przypiętego AMI.
- (−) Grupa bezpieczeństwa jest jedyną zaporą. Błąd w jej regułach (np. GT-10) nie ma drugiej warstwy na hoście.
- (−) Pełny benchmark utwardzania (np. CIS) jest poza zakresem. Skrypt obejmuje tylko kroki wybrane w tym ADR.
- Pusty katalog `infra/ansible/` usunięto (decyzja autora). Ansible znika z zakresu pracy, a książka *Ansible: Up and Running* z katalogu zadań nie jest potrzebna.
- E05-07 wdraża stos do katalogu `/opt/app` użytkownika `app`.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować), wszystkie sprawdzone 2026-11-11:

- Ansible, *Installing Ansible*: https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html
- Ansible, *amazon.aws.aws_ssm connection*: https://docs.ansible.com/ansible/latest/collections/amazon/aws/aws_ssm_connection.html
- Docker, *Packet filtering and firewalls*: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Docker, *Linux post-installation steps for Docker Engine*: https://docs.docker.com/engine/install/linux-postinstall/
- AWS, *Run commands when you launch an EC2 instance with user data input*: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
