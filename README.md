# Metody eksploracji danych w odkrywaniu wiedzy - projekt

* Mikołaj Garbowski
* Marcin Bagnowski

## Zadanie

1. Celem projektu jest implementacja jednego z algorytmów odkrywania zbiorów częstych, zamkniętych, maksymalnych lub
   rzadkich.
   Konkretny algorytm będzie przydzielony indywidualnie.
2. Język programowania dowolny.
3. Dane wejściowe i wyjściowe powinny być zgodne z formatem stosowanym w bibliotece SPMF:
   https://www.philippe-fournier-viger.com/spmf/
4. Należy porównać własną implementację (najlepiej w kilku wersjach, patrz punkt 5) z wersją dostępną w SPMF na
   wybranych zbiorach danych pod względem:
    * poprawności wyników,
    * wydajności (w szczególności czasu działania).

5. Należy zaproponować i przetestować proste optymalizacje, np. poprzez zastosowanie różnych typów danych lub struktur
   danych.

Proszę o zgłoszenie się do mnie w celu przydziału algorytmu (mailowo, teams, lub osobiście podczas konsultacji).

---

Proszę zaimplementować algorytm LCM (https://www.philippe-fournier-viger.com/spmf/LCM2.pdf) do odkrywania zbiorów
zamkniętych.
Termin do 16 czerwca. Bardzo zachęcam do przedstawienia wcześniej (nawet kilkakrotnie) cząstkowych wyników.

## Instrukcja uruchomienia

* Do uruchomienia skryptów Pythona jest używany [uv](https://docs.astral.sh/uv/) i [just](https://github.com/casey/just)
* Projekt ma minimalne zależności, sama implementacja wykorzystuje tylko bibliotekę standardową
* Do uruchomienia implementacji algorytmu z biblioteki SPMF wymagana jest instalacja Javy
    * biblioteka w pliku jar jest dołączona do repozytorium
    * testowe zbiory danych z SPMF są dołączone do repozytorium
* Komendy
    * Do wylistowania przez `just -l`
    * Instalacja zależności: `just install`
    * Uruchomienie testów: `just test`
    * Formatowanie kodu: `just fmt`
    * Analiza statyczna kodu: `just check`
    * Uruchomienie naszego algorytmu: `just run --help` (sprawdź parametry)
    * Profilowanie czasu działania i zużycia pamięci naszej implementacji: `just profile --help` (sprawdź parametry)
* Testy
    * testy jednostkowe implementacji algorytmu
    * testy porównujące wyniki naszej implementacji z wynikami implementacji SPMF (poprawność)
* Asercje a wydajność
    * w implementacji algorytmu są robione drogie asercje (np. sprawdzenie, czy elementy transakcji są posortowane)
    * to ma pomóc w testowaniu i debugowaniu
    * asercje można całkiem wyłączyć ustawiając zmienną środowiskową `PYTHONOPTIMIZE=1`
    * (to już jest załatwione jak się uruchamia `just profile`)

## Materiały

* [Dokumentacja SPMF](https://www.philippe-fournier-viger.com/spmf/)
* [Implementacja algorytmu LCM w SPMF](https://github.com/philfv9/spmf-software/blob/main/ca/pfv/spmf/algorithms/frequentpatterns/lcm/AlgoLCM.java)
* [Artykuł opisujący algorytm LCM](https://www.philippe-fournier-viger.com/spmf/LCM2.pdf)

## Wprowadzone optymalizacje

Algorytm LCM2 został zaimplementowany w dwóch podstawowych wersjach, czyli bez scalania jednakowych transakcji w jedną (klasy **LCMAlgorithm**, **Transaction**) oraz z mechanizmem scalania (klasy **LCMAlgorithmIntersec**, **TransactionIntersec**). Scalanie polega na złączaniu transakcji o tych samych elementach w części aktualnie analizowanej - znajdujących się na pozycjach dalszych niż _offset_. Przy scaleniu następuje zsumowanie wagi transakcji (bazowo = 1) oraz przecięcie elementów wspólnych między transakcjami (parametr _interior_intersection_). Jako, że algorytm z mechanizmem scalania działał wydajniej w większości przeprowadzonych testów wydajnościowych, to właśnie ta wersja została wybrana jako domyślna implementacja do dalszych analiz.

### Zastosowanie `__slots__`
Zamiast standardowego słownika `__dict__` do przechowywania atrybutów obiektu, w klasach reprezentujących transakcje oraz zbiory elementów wymuszono statyczną alokację pamięci. 
* **Miejsce zastosowania:** Klasa `TransactionOpt` (ręczna definicja `__slots__`) oraz `ItemsetOpt` (parametr dekoratora `@dataclass(slots=True)`).
* **Efekt:** Drastyczne zmniejszenie narzutu pamięciowego dla każdego obiektu transakcji i wynikowego zbioru (których w trakcie działania algorytmu powstają setki tysięcy) oraz przyspieszenie dostępu do atrybutów klasy.

### Zmiana struktury danych dla elementów transakcji (Tuple zamiast List)
Zmieniono typ przechowywanych elementów transakcji (`items`) z mutowalnej listy (`list[int]`) na niemutowalną krotkę (`tuple[int, ...]`).
* **Miejsce zastosowania:** Klasa `TransactionOpt` (metody `__init__` oraz `remove_infrequent_items`).
* **Efekt:** Krotki w języku Python mają mniejszy narzut pamięciowy niż listy i są szybciej alokowane. Dodatkowo, wycinki (slices) krotek mogą być bezpośrednio używane jako klucze w słownikach (są hashowalne), co wyeliminowało konieczność rzutowania typów podczas scalania.

### Jednoprzebiegowe scalanie transakcji i redukcja alokacji obiektów
Całkowicie przebudowano logikę przecinania i scalania transakcji. Wcześniej algorytm tworzył nowe obiekty transakcji, dodawał je do listy, a następnie w osobnej metodzie (`merge_transactions`) grupował je i scalał.
* **Miejsce zastosowania:** Metoda `intersect_transactions` w `LCMAlgorithmOpt`.
* **Efekt:** Obecnie filtrowanie, wycinanie odpowiednich fragmentów transakcji i ich scalanie odbywa się w **jednym przebiegu**. Zamiast tworzyć tymczasowe obiekty `TransactionOpt`, algorytm operuje na surowych danych w słowniku (`merged_dict`). Obiekty klas są instancjonowane tylko raz, na samym końcu, wyłącznie dla unikalnych (już scalonych) transakcji. Dodano również warunek wczesnego wyjścia (`if item not in t.interior_intersection: continue`).

### Optymalizacja redukcji bazy danych (Anytime Database Reduction)
Zoptymalizowano proces czyszczenia i ponownego wypełniania kubełków (buckets) dla częstych elementów.
* **Miejsce zastosowania:** Metoda `anytime_database_reduction` w `LCMAlgorithmOpt`.
* **Zmiany szczegółowe:**
  * **Struktura danych:** Zastąpiono wyszukiwanie w liście (`item in frequent_items` - złożoność $O(N)$) wyszukiwaniem w zbiorze (`valid_targets = set(...)` - złożoność $O(1)$), gdzie zbiór zawiera tylko elementy większe od aktualnie przetwarzanego
  * **Usunięcie redundantnych warunków:** Wyeliminowano warunek `item > item_e`, ponieważ zbiór `valid_targets` zawiera już wyłącznie odpowiednie elementy. Analogicznie, warunek `item in frequent_items` zastąpiono szybszym `item in valid_targets`.
  * **Early exit optimization:** Dodano sprawdzenie `if not valid_targets: return` na samym początku pętli, aby uniknąć niepotrzebnych operacji, gdy nie ma elementów do przetworzenia.
  * **Zmiana metody czyszczenia:** Zamiast tworzyć nowe obiekty list (`self.buckets[item] = []`), użyto metody `.clear()`, która wyczyszcza istniejące listy w miejscu, minimalizując alokacje pamięci.
* **Efekt:** Znaczące zmniejszenie złożoności czasowej metody oraz zmniejszenie alokacji pamięci dzięki ponownímu wykorzystaniu istniejących struktur danych.

### Eliminacja narzutu wywołań metod (Function call overhead)
Usunięto zbędne metody pomocnicze z klasy transakcji, przenosząc logikę bezpośrednio do miejsc ich wywołania.
* **Miejsce zastosowania:** Usunięcie metod `get_active_items_tuple()` oraz `with_offset()` z klasy `TransactionOpt`; bezpośrednie operacje w `intersect_transactions`.
* **Efekt:** W języku Python każde wywołanie metody wiąże się z narzutem wydajnościowym (tworzenie ramki stosu). Dzięki temu, że `items` jest teraz krotką, algorytm może bezpośrednio i błyskawicznie wycinać jej fragmenty (`key = t.items[pos:]`) jako klucze do słownika, całkowicie omijając kosztowne wywoływanie dodatkowych metod wewnątrz najbardziej obciążonych pętli.

### Tymczasowe wyłączenie Garbage Collectora (GC)
Algorytm LCM opiera się na głębokiej rekurencji i tworzy ogromną liczbę krótkotrwałych obiektów (np. wycinki list, zbiory). Domyślne działanie Garbage Collectora w Pythonie powodowało częste, niepotrzebne pauzy w działaniu programu.
* **Miejsce zastosowania:** Metody `__init__` (wywołanie `gc.disable()`) oraz `close()` (wywołanie `gc.enable()`) w `LCMAlgorithmOpt`.
* **Efekt:** Znaczące skrócenie całkowitego czasu wykonania algorytmu poprzez odłożenie zwalniania pamięci do momentu zakończenia intensywnych obliczeń.

### Mikrooptymalizacje pętli i lokalne referencje do metod
Wyeliminowano narzut związany z wywoływaniem wbudowanych funkcji Pythona oraz wyszukiwaniem atrybutów w przestrzeni nazw klas.
* **Miejsce zastosowania:** Metody `is_ppc_extension`, `is_item_in_all_transactions` oraz `backtracking_lcm`.
* **Efekt:** 
  * Zastąpiono funkcję `all()` z wyrażeniem generatorowym jawnymi pętlami `for` z wczesnym wyjściem (`return False`). W CPythonie jawna pętla jest szybsza niż tworzenie ramki generatora dla małych kolekcji.
  * W metodzie `is_ppc_extension` przypisano statyczną metodę do zmiennej lokalnej (`check = LCMAlgorithmOpt.is_item_in_all_transactions_except_first`), co przyspiesza jej wywoływanie wewnątrz pętli (szybszy *name lookup*).

### Zastąpienie pętli `for` z `.append()` wyrażeniami typu Comprehensions
Wyeliminowano klasyczne pętle `for`, w których warunkowo dodawano elementy do nowej listy za pomocą metody `.append()`, zastępując je natywnymi wyrażeniami składanymi.
* **Miejsca zastosowania:** 
  * **Tworzenie `new_frequent_items`** w metodzie `backtracking_lcm` (zastąpienie wielolinijkowej pętli z warunkiem `if` jednym *list comprehension*).
  * **Filtrowanie elementów transakcji** w metodzie `remove_infrequent_items` w klasie `TransactionOpt` (użyto *generator expression* przekazanego bezpośrednio do konstruktora `tuple()`).
  * **Zwracanie scalonych transakcji** na końcu metody `intersect_transactions` (zamiast iterować po słowniku i dodawać nowe obiekty `TransactionOpt` do listy za pomocą `.append()`, cała lista wynikowa jest budowana w locie za pomocą *list comprehension* iterującego po `merged_dict.values()`).
* **Efekt:** Wyrażenia składane w języku Python są zaimplementowane i wykonywane na poziomie języka C. Sprawia to, że alokacja pamięci dla nowej kolekcji oraz jej wypełnianie są zauważalnie szybsze niż wielokrotne wywoływanie metody `.append()` w każdej iteracji pętli na poziomie interpretera Pythona. W przypadku `intersect_transactions` pozwoliło to na błyskawiczne instancjonowanie tysięcy obiektów w jednym kroku.

### Zastąpienie wyrażeń generatorowych na List comprehensions
W miejscach agregacji danych (np. sumowanie wag transakcji) zmieniono podejście do przekazywania danych.
* **Miejsce zastosowania:** Metoda `backtracking_lcm` (np. `sum([t.weight for t in transactions_of_union])`).
* **Efekt:** Choć generatory oszczędzają pamięć, w implementacji CPython przekazanie gotowej listy (stworzonej przez szybkie *list comprehension* w C) do funkcji `sum()` wykonuje się szybciej niż iterowanie po generatorze element po elemencie.

### Leniwe wczytywanie plików i redukcja alokacji
Zrezygnowano z wczytywania całego pliku do pamięci za pomocą metody `io.readlines()` (która tworzyła ogromną listę stringów w pamięci RAM) na rzecz bezpośredniej iteracji po obiekcie strumienia (`for line in io`). Dodatkowo usunięto wywołanie `.strip()`, ponieważ bezargumentowe `.split()` domyślnie ignoruje wszelkie białe znaki, w tym znaki nowej linii.
* **Miejsce zastosowania:** Metoda `from_stream` w klasie `DatasetOpt`.
* **Efekt:** Drastyczne zmniejszenie zużycia pamięci RAM podczas inicjalizacji algorytmu (szczególnie przy gigabajtowych zbiorach danych) oraz przyspieszenie parsowania pliku wejściowego.

### Wykorzystanie wbudowanej funkcji `map()` zamiast pętli w Pythonie
Zastąpiono wyrażenia listowe i generatorowe (np. `[int(num) for num in ...]`, `(str(item) for item in ...)`) wywołaniami wbudowanej funkcji `map()` (odpowiednio: `map(int, line.split())` oraz `map(str, self.items)`).
* **Miejsce zastosowania:** 
  * Parsowanie linii pliku w metodzie `from_stream` w klasie `DatasetOpt`.
  * Formatowanie wyników w metodzie `to_spmf_line` w klasie `ItemsetOpt`.
* **Efekt:** Funkcja `map()` jest zaimplementowana bezpośrednio w języku C. Rzutowanie typów (ze stringa na int przy wczytywaniu danych i z int na string przy zapisie) za jej pomocą jest zauważalnie szybsze i bardziej zoptymalizowane pod kątem pamięci niż wykonywanie tych samych operacji w pętli na poziomie interpretera Pythona.

### Grupowe aktualizowanie zbiorów
Zamiast iterować po każdym elemencie transakcji w zagnieżdżonej pętli `for` i dodawać go pojedynczo do zbioru unikalnych elementów (`unique_items.add(item)`), zastosowano metodę `.update()`, przekazując jej całą kolekcję.
* **Miejsce zastosowania:** Metoda `_get_unique_items_from_transactions` w klasie `DatasetOpt`.
* **Efekt:** Metoda `.update()` wykonuje pętlę dodającą elementy na poziomie języka C, co eliminuje narzut związany z wywoływaniem metody `.add()` w Pythonie dla każdego pojedynczego elementu.

### Optymalizacja wyszukiwania w funkcji `contains_after()`
Zoptymalizowano funkcję `contains_after()` w module `utils` poprzez dodanie wczesnego wyjścia (early exit) w iteracji.
* **Miejsce zastosowania:** Funkcja `contains_after()` w module `lcm_opt/utils.py`.
* **Efekt:** W najgorszym przypadku złożoność pozostaje $O(N)$, ale w praktyce algorytm średnio kończy pracę wcześniej, szczególnie gdy szukany element znajduje się wśród mniejszych indeksów.

### Uproszczenie warunku logicznego w metodzie `is_ppc_extension()`
Zoptymalizowano warunek logiczny w metodzie `is_ppc_extension()` poprzez eliminację redundantnego warunku - usunięcie `len(prefix) == 0`, który i tak pokrywa `item not in prefix`.
* **Miejsce zastosowania:** Metoda `is_ppc_extension()` w klasie `LCMAlgorithmOpt`.
* **Efekt:** Nieznaczne, ale mierzalne przyspieszenie, szczególnie w gęstych zbiorach danych, gdzie `is_ppc_extension()` jest wywoływana bardzo często.


## Benchmarki

W celu porównania wydajności zaimplementowanych wersji algorytmu przeprowadzono serię benchmarków mierzących czas wykonania oraz zużycie pamięci dla różnych wartości minimalnego wsparcia.

Porównano następujące implementacje:

* **SPMF** — implementacja biblioteczna,
* **custom** — podstawowa własna implementacja algorytmu,
* **intersec** — wersja wykorzystująca scalanie/przecięcia transakcji,
* **optimized (file)** — wersja zoptymalizowana z bieżącym zapisem wyników do pliku,
* **optimized (memory)** — wersja zoptymalizowana z buforowaniem wyników w pamięci.

Dla każdej konfiguracji benchmark został wykonany **trzykrotnie**, a w tabelach przedstawiono średni czas wykonania wraz z odchyleniem standardowym.

Pomiary pamięci zostały wykonane przy użyciu modułu `tracemalloc`.
W przypadku implementacji **SPMF** pomiary zużycia pamięci nie zostały uwzględnione, ponieważ algorytm wykonywany jest wewnątrz maszyny wirtualnej JVM, a użyte narzędzia profilujące mierzyły wyłącznie pamięć alokowaną po stronie interpretera Python.

Implementacje przetestowano na trzech różnych typach zbiorów:
- [**`Retail`**](#zbiór-danych-retail) - zbiór rzadki - bardzo mało pokrywających się transakcji
- [**`Chess`**](#zbiór-danych-chess) - zbiór gęsty - wiele pokrywających się transakcji
- [**`Pubmsb`**](#zbiór-danych-pubmsb) - zbiór ogólny - średnio gęsty z zdecydowanie dłuższymi transakcjami

Wartości wsparcia dla przeprowadzonych pomiarów zostały dobrane odpowiednio dla każdego zbioru, aby pasowały do jego charakterystyki.

Wszystkie wykorzystane zbiory pochdzą ze strony [https://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php#d2](https://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php#d2).

---

### Zbiór danych: `Retail`

Zbiór danych o następującej charakterystyce:

| Parametr                              | Wartość  |
|---------------------------------------|----------|
| Liczba transakcji                     | `88 162` |
| Liczba unikalnych elementów           | `16 470` |
| Średnia liczba elementów w transakcji | `10,30`  |
| Gęstość zbioru                        | `0,06 %` |

#### Czas wykonania (ms)

| Row                | 70%             | 80%             | 90%             |
|:-------------------|:----------------|:----------------|:----------------|
| Intersec (file)    | 1362.47 ± 23.54 | 1356.09 ± 17.60 | 1371.28 ± 28.26 |
| Intersec (memory)  | 1374.94 ± 30.33 | 1372.76 ± 25.23 | 1377.60 ± 23.03 |
| Optimized (file)   | 1141.38 ± 21.24 | 1133.86 ± 19.78 | 1131.10 ± 15.33 |
| Optimized (memory) | 1174.91 ± 22.33 | 1179.43 ± 20.56 | 1174.02 ± 27.89 |
| SPMF (file)        | 37.76 ± 3.31    | 38.24 ± 4.61    | 37.88 ± 4.88    |

### Zużycie pamięci (MB)

| Row                | 70%           | 80%           | 90%           |
|:-------------------|:--------------|:--------------|:--------------|
| Intersec (file)    | 117.80 ± 0.00 | 117.80 ± 0.00 | 117.80 ± 0.00 |
| Intersec (memory)  | 117.79 ± 0.00 | 117.79 ± 0.00 | 117.79 ± 0.00 |
| Optimized (file)   | 111.93 ± 0.00 | 111.93 ± 0.00 | 111.93 ± 0.00 |
| Optimized (memory) | 111.93 ± 0.00 | 111.93 ± 0.00 | 111.93 ± 0.00 |
| SPMF (file)        | 49.95 ± 0.93  | 50.17 ± 1.10  | 50.25 ± 0.95  |

---

### Zbiór danych: `Chess`

Zbiór danych o następującej charakterystyce:

| Parametr                              | Wartość   |
|---------------------------------------|-----------|
| Liczba transakcji                     | `3 196`   |
| Liczba unikalnych elementów           | `75`      |
| Średnia liczba elementów w transakcji | `37`      |
| Gęstość zbioru                        | `49,33 %` |

#### Czas wykonania (ms)

| Row                | 70%             | 80%            | 90%           |
|:-------------------|:----------------|:---------------|:--------------|
| Intersec (file)    | 3880.66 ± 36.51 | 800.32 ± 13.03 | 271.55 ± 4.83 |
| Intersec (memory)  | 3921.05 ± 40.36 | 801.95 ± 15.64 | 267.88 ± 5.28 |
| Optimized (file)   | 2109.95 ± 14.44 | 460.55 ± 2.93  | 171.52 ± 1.45 |
| Optimized (memory) | 2096.27 ± 15.42 | 456.15 ± 2.38  | 171.43 ± 1.11 |
| SPMF (file)        | 3581.44 ± 55.66 | 753.64 ± 18.09 | 124.80 ± 7.51 |

#### Zużycie pamięci (MB)

| Row                | 70%            | 80%           | 90%          |
|:-------------------|:---------------|:--------------|:-------------|
| Intersec (file)    | 16.36 ± 0.11   | 10.07 ± 0.01  | 9.32 ± 0.00  |
| Intersec (memory)  | 21.64 ± 0.02   | 11.14 ± 0.01  | 9.32 ± 0.00  |
| Optimized (file)   | 11.12 ± 0.09   | 9.11 ± 0.00   | 9.10 ± 0.00  |
| Optimized (memory) | 16.58 ± 0.09   | 9.10 ± 0.00   | 9.10 ± 0.00  |
| SPMF (file)        | 319.99 ± 31.32 | 296.37 ± 0.11 | 75.67 ± 0.34 |

---

### Zbiór danych: `Pubmsb`

Zbiór danych o następującej charakterystyce:

| Parametr                              | Wartość  |
|---------------------------------------|----------|
| Liczba transakcji                     | `49 046` |
| Liczba unikalnych elementów           | `2113`   |
| Średnia liczba elementów w transakcji | `74`     |
| Gęstość zbioru                        | `3,50 %` |

#### Czas wykonania (ms)

| Row                | 90%               |
|:-------------------|:------------------|
| Intersec (file)    | 13344.28 ± 201.02 |
| Intersec (memory)  | 13341.45 ± 201.52 |
| Optimized (file)   | 5232.52 ± 72.51   |
| Optimized (memory) | 5295.16 ± 100.26  |
| SPMF (file)        | 8102.80 ± 49.60   |

#### Zużycie pamięci (MB)

| Row                | 90%            |
|:-------------------|:---------------|
| Intersec (file)    | 245.12 ± 0.00  |
| Intersec (memory)  | 245.12 ± 0.00  |
| Optimized (file)   | 242.13 ± 0.00  |
| Optimized (memory) | 242.12 ± 0.00  |
| SPMF (file)        | 601.65 ± 43.23 |
