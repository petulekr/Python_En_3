# Elections Scraper
Cílem projektu je vytvořti scraper, který získá výsledky z parlamentních voleb z roku 2017 přímo z webu.

## Instalace knihoven
Knihovny použité ve scriptu jsou dostupné v souboru requirements.txt

## Spuštění souboru
Soubor se spouští pomocí příkazového řádku s dvěma argumenty:
python elections_2017_scraper.py "<odkaz_uzemniho_celku>" "<vystupni_soubor>"

## Ukázka spuštění souboru
python elections_2017_scraper.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_prostejov.csv"
