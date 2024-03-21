# Testovanie YAML servera

## Čo urobiť pred testovaním

1. Je treba nainštalovať pythonovskú knižnicu `pygments`.
2. Musíte mať nainštalovanú aj knižnicu `ncurses`, ale tú takmer iste nainštalovanú máte.
3. Potrebujete nainštalovať aj príkaz `rkill`, ktorý je pravdepodobne v balíčku `pslist`

## Ako testovať hromadne všetky testy

1. Skopírujte do tohto adresára váš program a nazvite ho `yaml_server.py`.
2. Spustite skript `runtests.sh`.
3. Spustia sa testy. Počkajte, kým dobehnú, pár sekúnd to trvá.
4. Vznikne súbor `results.html`, ktorý si môžete otvoriť v browseri.
5. Pre každý test máte pod linkom uvedené, čo sa posielalo a v akom stave skončil.
6. Ak bol nejaký chybový výstup (niečo padlo), chybový výstup vidíte pod linkom err.

## Čo robiť ak niečo nejde

Ak Vám to testovanie nejde, ozvite sa mi buď emailom alebo napíšte issue do tohto projektu na githube zistíme, kde je problém.
