# uni
Programmatūras ieviešanas un uzturēšanas dzīves cikls un procesu automatizācija

## Project description

This project is a desktop student management application. It is designed
to demonstrate software implementation, maintenance, database integration, and
process automation practices.

The project is written in **Python** and uses **MySQL** to store student
records. Database schema changes are managed with **Alembic migrations**, and
database credentials are loaded from environment variables instead of being
stored in the source code.

The main application is a graphical Tkinter program. The code is organized
into an `app` package so the interface, database queries, and validation rules
are separate:

```text
app/
├── database.py   # MySQL connection and student repository
├── gui.py        # Tkinter interface
└── validators.py # Input validation
config.py         # Environment-based configuration
gui.py            # Simple GUI launcher
main.py           # Terminal application
migrations/       # Database schema migrations
tests/            # Automated tests
docs/             # Project notes and text templates
logs/             # Local application logs
```

The root launcher files and configuration files stay in the project root so
Python, Alembic, and the setup instructions can find them without extra path
configuration.

The application can:

- Add new students with a name, email address, date of birth, study program,
  phone number, and enrollment date.
- Display all students stored in the database.
- Update an existing student's details.
- Delete a student after confirmation.
- Open a detailed student profile.
- Search by name, email, study program, or phone number.
- Sort records by clicking a table heading.
- Navigate records with pagination.
- Validate names, email addresses, dates, study programs, and phone numbers.
- Prevent duplicate email addresses.
- Log important application actions and errors to `student_manager.log`.
- Run automated unit and database integration tests.

The project uses a simple interactive terminal menu. It is suitable for
learning basic Python programming, CRUD operations, relational databases,
input validation, migrations, logging, testing, and secure configuration
management.

# Git practice

## Usage - Team update

Run the Git practice program with:

```powershell
python src/main.py
```

## Projekta palaišana

### Priekšnosacījumi

- Python 3.13 vai jaunāks.
- Darbojošs MySQL serveris.
- Izveidota datubāze `student_manager`.

### Instalēšana

PowerShell terminālī projekta mapē izveido un aktivizē virtuālo vidi:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Instalē projekta atkarības:

```powershell
pip install -r requirements.txt
```

### Datubāzes konfigurācija

Datubāzes iestatījumi tiek nolasīti no vides mainīgajiem, tāpēc paroles un citi
savienojuma dati nav jāieraksta `config.py`. Izveido lokālu `.env` failu,
balstoties uz [`.env.example`](.env.example), vai iestati mainīgos PowerShell
sesijā:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "your_mysql_user"
$env:DB_PASSWORD = "your_mysql_password"
$env:DB_NAME = "student_manager"
```

`.env` ir iekļauts `.gitignore`, tāpēc tas netiks pievienots repozitorijam.
Nekad nepublicē paroles vai citus noslēpumus Git repozitorijā.

MySQL Workbench vai citā MySQL klientā izveido datubāzi:

```sql
CREATE DATABASE student_manager;
```

Pēc tam projekta mapē izpildi visas migrācijas:

```powershell
alembic upgrade head
```

Alembic izmanto tos pašus `DB_HOST`, `DB_USER`, `DB_PASSWORD` un `DB_NAME`
mainīgos no `.env`, ko izmanto programma. `alembic.ini` vairs nav jāieliek
parole.

### Programmas palaišana

```powershell
python main.py
```

Programma ļauj pievienot, apskatīt, atjaunināt un dzēst studentus. Darbību
žurnāls tiek saglabāts failā `student_manager.log`.

### Grafiskā saskarne

Projektam ir arī grafiska Tkinter saskarne ar logu, tabulu, pogām un
ziņojumiem par kļūdām. Tā izmanto to pašu MySQL datubāzi un `.env`
konfigurāciju:

```powershell
python gui.py
```

Grafiskajā saskarnē var pievienot, apskatīt, atjaunināt, dzēst, meklēt, kārtot,
profilā apskatīt un pārlādēt studentu ierakstus. Lai atjauninātu, dzēstu vai
atvērtu profilu, vispirms izvēlies studentu tabulā. Datumi jāievada formātā
`DD/MM/YYYY`.

`main.py` un `gui.py` abi palaiž grafisko lietotni. Vecā termināļa
implementācija ir saglabāta `app/legacy_cli.py` tikai vēsturei un vairs nav
aktīvā palaišanas metode, jo datubāzes struktūra tagad izmanto dzimšanas
datumu, nevis vecumu.

### Testu palaišana

Validācijas unit testus var palaist bez MySQL savienojuma:

```powershell
python -m unittest -v tests.test_validators
```

Pilno studentu izveides, nolasīšanas, atjaunināšanas, dublikāta e-pasta,
dzēšanas un dzēšanas pārbaudes testu var palaist tikai atsevišķā testa
datubāzē. `.env` failā norādi testa datubāzi un pirms testa iestati:

```powershell
$env:RUN_DB_TESTS = "1"
$env:TEST_DB_NAME = "student_manager_test"
python -m unittest -v tests.test_student_database
```

Testa datubāzei jābūt izveidotai un jāizmanto tā pati migrāciju struktūra kā
`student_manager` datubāzei. Tests izveido `students` tabulu, ja tā vēl
neeksistē, un pēc katra testa izdzēš testa ierakstus.

## Projekta izstrādes vēsture

1. **Initial commit** - izveidots repozitorijas sākotnējais stāvoklis.
2. **Initial project structure** - izveidota projekta pamatstruktūra un nepieciešamie sākotnējie faili.
3. **Add virtual environment and dependencies** - pievienota virtuālā Python vide un projekta atkarību saraksts.
4. **Add database configuration** - pievienoti MySQL datubāzes savienojuma konfigurācijas iestatījumi.
5. **Add MySQL connection test** - pārbaudīts, vai programma var izveidot savienojumu ar MySQL datubāzi.
6. **Initialize database migrations** - projektam pievienota Alembic migrāciju sistēma datubāzes struktūras pārvaldībai.
7. **Create students table migration** - izveidota migrācija `students` tabulai ar ID, vārda un e-pasta laukiem.
8. **Add age column migration** - izveidota migrācija studentu vecuma lauka pievienošanai.
9. **Add student management menu** - izveidota interaktīva izvēlne studentu pievienošanai, apskatei un programmas aizvēršanai.
10. **Complete second migration** - pabeigta un papildināta datubāzes migrācija ar studentu vecuma lauku.
11. **Add GitHub Actions automation** - pievienota automātiska projekta pārbaude, izmantojot GitHub Actions.
12. **Add delete student feature** - pievienota iespēja dzēst studentu pēc tā ID.
13. **Improve student display** - uzlabots studentu saraksta attēlojums ar virsrakstiem un sakārtotu tabulas formātu.
14. **Age error handeling** - pievienota vecuma ievades pārbaude, lai nederīgas vērtības netiktu saglabātas kā skaitlis.
15. **Move database settings to environment** - datubāzes iestatījumi pārcelti uz vides mainīgajiem, lai konfigurācija būtu elastīgāka.
16. **README.md dokuments** - README failam pievienots projekta izstrādes vēstures apraksts.
17. **Move database settings to enviroment fix** - izlabota datubāzes iestatījumu pārcelšanas implementācija.
18. **README.md dokuments** - papildināts apraksts.
19. **Email Validation** - pievienota e-pasta pārbaude, kas pieprasa `@` simbola esamību.
20. **database fix** - izlabota datubāzes konfigurācija.
21. **Name validation** - pievienota vārda pārbaude, kas nepieļauj tukšu ievadi.
22. **Delete Validation** - pievienots apstiprinājums pirms studenta dzēšanas.
23. **Duplicate email checking.** - pievienota pārbaude, kas neļauj reģistrēt jau izmantotu e-pasta adresi.
24. **Student update feature** - pievienota iespēja mainīt esoša studenta vārdu, e-pastu un vecumu.
25. **Age range validation** - vecuma ievade ierobežota diapazonā no 0 līdz 120.
26. **Action logging** - pievienota programmas darbību reģistrēšana failā `student_manager.log`.
27. **Database connection error handling** - pievienota MySQL savienojuma kļūdu apstrāde ar saprotamu paziņojumu.
28. **Add unit tests for validation** - pievienoti unit testi vārda, e-pasta un vecuma validācijas pārbaudei.
29. **Handle invalid menu choice** - pievienota kļūdas apstrāde nederīgai izvēlnes izvēlei.
30. **Update README setup instructions** - README papildināts ar instalēšanas, datubāzes konfigurācijas, migrāciju, palaišanas un testu instrukcijām.
31. **Complete GUI student interface** - izveidota pilna Tkinter grafiskā saskarne studenta ierakstu pārvaldībai.
32. **Modularize application code** - kods sadalīts `app` pakotnē: datubāzes piekļuve, grafiskā saskarne un validācija atdalīti atsevišķos moduļos.
33. **Expand student data model** - vecuma lauks aizstāts ar dzimšanas datumu, studiju programmu, tālruņa numuru un uzņemšanas datumu.
34. **Add student profile and search** - pievienots detalizēts studenta profils, meklēšana un ierakstu kārtošana pēc tabulas virsrakstiem.
35. **Add pagination and GUI tests** - pievienota lapošana studenta sarakstā un automātiski testi GUI ierakstu izveidei un atjaunināšanai.
36. **Secure repository configuration** - datubāzes un virtuālās vides faili izslēgti no Git izsekošanas, bet pievienota droša `.env.example` konfigurācijas veidne.
37. **Clean repository and final documentation** - noņemtas palīgfailu parādības, atjaunināts README, projekta struktūra un palaišanas instrukcijas.
