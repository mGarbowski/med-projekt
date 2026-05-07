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
Proszę implementować algorytm LCM (https://www.philippe-fournier-viger.com/spmf/LCM2.pdf) do odkrywania zbiorów
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

## TODO

* Optymalizacje algorytmu
    * na pewno wyszukiwanie binarne w wielu miejscach
    * aktualna implementacja jest wzorowana na SPMF
    * chyba dałoby się wyrzucić referencję `original_transaction` z klasy `Transaction`
    * zapisy wyników do pliku pewnie można by jakoś buforować
* Na jakich zbiorach profilować algorytm?
    * te, które są dołączone mają po kilka przykładów
* Jak profilować algorytm?
    * czy ładowanie zbioru danych też liczymy
    * czy profilujemy z zapisywaniem wyników do pliku (więcej czasu) czy z przechowywaniem wyników w pamięci (więcej
      pamięci)

## Wyniki

| Implementation | Dataset           | Mode   | Support | Time Mean (ms) | Time Std (ms) | Memory Mean (MB) | Memory Std (MB) |
|:---------------|:------------------|:-------|:--------|:---------------|:--------------|:-----------------|:----------------|
| SPMF           | dense-chess.txt   | file   | 70%     | 3581.44        | 55.66         | 319.99           | 31.32           |
| SPMF           | dense-chess.txt   | file   | 80%     | 753.64         | 18.09         | 296.37           | 0.11            |
| SPMF           | dense-chess.txt   | file   | 90%     | 124.8          | 7.51          | 75.67            | 0.34            |
| SPMF           | sparse-retail.txt | file   | 70%     | 37.76          | 3.31          | 49.95            | 0.93            |
| SPMF           | sparse-retail.txt | file   | 80%     | 38.24          | 4.61          | 50.17            | 1.1             |
| SPMF           | sparse-retail.txt | file   | 90%     | 37.88          | 4.88          | 50.25            | 0.95            |
| SPMF           | general-pumsb.txt | file   | 90%     | 8102.8         | 49.6          | 601.65           | 43.23           |
| Optimized      | dense-chess.txt   | file   | 70%     | 2109.95        | 14.44         | 11.12            | 0.09            |
| Optimized      | dense-chess.txt   | file   | 80%     | 460.55         | 2.93          | 9.11             | 0.00            |
| Optimized      | dense-chess.txt   | file   | 90%     | 171.52         | 1.45          | 9.10             | 0.00            |
| Optimized      | dense-chess.txt   | memory | 70%     | 2096.27        | 15.42         | 16.58            | 0.09            |
| Optimized      | dense-chess.txt   | memory | 80%     | 456.15         | 2.38          | 9.10             | 0.00            |
| Optimized      | dense-chess.txt   | memory | 90%     | 171.43         | 1.11          | 9.10             | 0.00            |
| Optimized      | general-pumsb.txt | file   | 70%     | 89003.72       | 827.53        | 242.13           | 0.00            |
| Optimized      | general-pumsb.txt | file   | 80%     | 9813.63        | 98.16         | 242.13           | 0.00            |
| Optimized      | general-pumsb.txt | file   | 90%     | 5232.52        | 72.51         | 242.13           | 0.00            |
| Optimized      | general-pumsb.txt | memory | 70%     | 83596.09       | 1382.38       | 259.88           | 0.14            |
| Optimized      | general-pumsb.txt | memory | 80%     | 9786.79        | 95.78         | 242.12           | 0.00            |
| Optimized      | general-pumsb.txt | memory | 90%     | 5295.16        | 100.26        | 242.12           | 0.00            |
| Optimized      | sparse-retail.txt | file   | 70%     | 1141.38        | 21.24         | 111.93           | 0.00            |
| Optimized      | sparse-retail.txt | file   | 80%     | 1133.86        | 19.78         | 111.93           | 0.00            |
| Optimized      | sparse-retail.txt | file   | 90%     | 1131.10        | 15.33         | 111.93           | 0.00            |
| Optimized      | sparse-retail.txt | memory | 70%     | 1174.91        | 22.33         | 111.93           | 0.00            |
| Optimized      | sparse-retail.txt | memory | 80%     | 1179.43        | 20.56         | 111.93           | 0.00            |
| Optimized      | sparse-retail.txt | memory | 90%     | 1174.02        | 27.89         | 111.93           | 0.00            |
| Intersec       | dense-chess.txt   | file   | 70%     | 3880.66        | 36.51         | 16.36            | 0.11            |
| Intersec       | dense-chess.txt   | file   | 80%     | 800.32         | 13.03         | 10.07            | 0.01            |
| Intersec       | dense-chess.txt   | file   | 90%     | 271.55         | 4.83          | 9.32             | 0.00            |
| Intersec       | dense-chess.txt   | memory | 70%     | 3921.05        | 40.36         | 21.64            | 0.02            |
| Intersec       | dense-chess.txt   | memory | 80%     | 801.95         | 15.64         | 11.14            | 0.01            |
| Intersec       | dense-chess.txt   | memory | 90%     | 267.88         | 5.28          | 9.32             | 0.00            |
| Intersec       | general-pumsb.txt | file   | 90%     | 13344.28       | 201.02        | 245.12           | 0.00            |
| Intersec       | general-pumsb.txt | memory | 90%     | 13341.45       | 201.52        | 245.12           | 0.00            |
| Intersec       | sparse-retail.txt | file   | 70%     | 1362.47        | 23.54         | 117.80           | 0.00            |
| Intersec       | sparse-retail.txt | file   | 80%     | 1356.09        | 17.60         | 117.80           | 0.00            |
| Intersec       | sparse-retail.txt | file   | 90%     | 1371.28        | 28.26         | 117.80           | 0.00            |
| Intersec       | sparse-retail.txt | memory | 70%     | 1374.94        | 30.33         | 117.79           | 0.00            |
| Intersec       | sparse-retail.txt | memory | 80%     | 1372.76        | 25.23         | 117.79           | 0.00            |
| Intersec       | sparse-retail.txt | memory | 90%     | 1377.60        | 23.03         | 117.79           | 0.00            |

## Materiały

* [Dokumentacja SPMF](https://www.philippe-fournier-viger.com/spmf/)
* [Implementacja algorytmu LCM w SPMF](https://github.com/philfv9/spmf-software/blob/main/ca/pfv/spmf/algorithms/frequentpatterns/lcm/AlgoLCM.java)
* [Artykuł opisujący algorytm LCM](https://www.philippe-fournier-viger.com/spmf/LCM2.pdf)
