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

## Materiały

* [Dokumentacja SPMF](https://www.philippe-fournier-viger.com/spmf/)
* [Implementacja algorytmu LCM w SPMF](https://github.com/philfv9/spmf-software/blob/main/ca/pfv/spmf/algorithms/frequentpatterns/lcm/AlgoLCM.java)
* [Artykuł opisujący algorytm LCM](https://www.philippe-fournier-viger.com/spmf/LCM2.pdf)
