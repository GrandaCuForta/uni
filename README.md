# uni
Programmatūras ieviešanas un uzturēšanas dzīves cikls un procesu automatizācija

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

Pirms palaišanas atver `config.py` un norādi sava MySQL servera iestatījumus:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "TAVA_MYSQL_PAROLE"
DB_NAME = "student_manager"
```

MySQL Workbench vai citā MySQL klientā izveido datubāzi:

```sql
CREATE DATABASE student_manager;
```

Pēc tam projekta mapē izpildi visas migrācijas:

```powershell
alembic upgrade head
```

### Programmas palaišana

```powershell
python main.py
```

Programma ļauj pievienot, apskatīt, atjaunināt un dzēst studentus. Darbību žurnāls tiek saglabāts failā `student_manager.log`.

### Testu palaišana

Validācijas unit testus var palaist bez MySQL savienojuma:

```powershell
python -m unittest -v test_validators.py
```

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


