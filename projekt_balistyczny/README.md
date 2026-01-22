## Uruchomienie: w folderze głównym projektu ~/projekt_balistyczny wpisać: python3 main.py - do obsługi stworzono menu w terminalu.

## Poprawki w piątek-sobotę:
- serializacja przez msgpack - zapis wyników i następnie odczyt historii symulacji
- automatyzacja - "wielokrotny_model_bc.py" - Za pomocą FOR uruchamiane są kolejne modele a potem sprawdzany jest warunek przekroczenia wartości współczynnika CD.





## Projekt z wykorzystaniem biblioteki do symulacji balistycznych
Projekt umożliwia prowadzenie symulacji toru lotu pocisku z wykorzystaniem modelu fizycznego balistyki, opartego na bibliotece 'py_ballistics'.
Programy są zbudowane w oparciu o przykłady z Example.ipynb i są wywoływane z terminala.

Z poziomu terminala użytkownik może:
- wybrać konfigurację naboju z pliku '.json' (masa, prędkość początkowa, współczynnik oporu)
- uruchomić program symulacji
- zapisać wyniki jako plik: '.png', '.json' oraz poprzez '.msgpack'
- wyświetlić wcześniejsze wyniki dzięki historii symulacji ('msgpack')

## Biblioteki
- 'py_ballistics' – biblioteka balistyczna (żeby uniknąć korzystania z środowiska wirtualnego bibliotekę sklonowałem lokalnie w projekcie)
- 'numpy', 'pandas', 'matplotlib' – przetwarzanie danych i wykresy
- 'subprocess', 'os', 'json' – automatyczne uruchamianie (run), obsługa terminala i przesyłanie danych konfiguracji i wyników, ścieżka do folderów biblioteki
- 'msgpack' – serializacja danych

## Programy symulacyjne (symulacje/)
- zerowanie_proste.py - Oblicza wymagany kąt uniesienia lufy, aby pocisk trafił w cel na zadanym dystansie.
- trajektoria_zagrozenia.py - Używana jest funkcja 'danger_space()' z 'py_ballisticcalc'. Wyznacza tor pocisku i oblicza tzw. *danger space* – czyli odcinek, na którym wysokość toru znajduje się wewnątrz określonego zakresu.
- rozwiazanie_z_karty.py - Umożliwia wykorzystanie gotowej tabeli trajektorii (range card) do obliczenia niezbędnej korekty celownika przy zmianie dystansu.
- rozwiazanie_z_kata.py - Symuluje strzelanie do celu widzianego pod kątem.
- wielokrotny_model_bc.py - Porównuje różne modele oporu aerodynamicznego z biblioteki ('DragModelMultiBC') dla standardów G1 i G7 (jedno- i wielopunktowe). Za pomocą FOR uruchamiane są kolejne modele a potem sprawdzany jest warunek przekroczenia wartości współczynnika CD.