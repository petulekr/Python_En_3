"""
projekt_3.py
discord: petulek
"""
import requests
import bs4
from bs4 import BeautifulSoup
import csv
import os
import sys


""" 
Global variables (lists) - cities for list of citites, hrefs for list of links
"""
cities = []
hrefs = []


def get_href(root: str, link: str, shift: int) -> str:
    """
    The function returns a link to the town of the territorial unit or detailed  of the town.
    :param root: https:\\
    :param link: specific town¨s link
    :param shift: the position of the first character of the second part of the link, so it subsequently ends with the character "
    :return: specific link
    """
    link = link[shift:link[shift:len(link)].find('"') + shift]
    link = root + link.replace('amp;', '')
    return link


def get_cities() -> None:
    """
    The function get_cities returns 2 lists - list of cities (cities) and list of links (hrefs) from page 'https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ'.
    :param flag: skips the line following the line containing the name of the territorial unit.
    """
    request = requests.get('https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ')
    if request.status_code == 200:
        flag = -1
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        for item in soup.find_all('td'):
            flag += 1
            if len(item.get_text()) > 1 and not item.get_text().startswith('CZ'):
                cities.append(item.get_text())
                flag = 0
            if flag == 2:
                hrefs.append(get_href('https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&', str(item.find('a')), 28))


def get_towns(i) -> dict:
    """
    The function get_towns return 1 dictionary, where key is town name and values are lists containing the town code and town link with th election result. 
    :param flag: provides line skipping according to the contents of the sup variable
    :return: specific dictionary with towns nad links
    """
    town_dict = {}
    town_href = ''
    town_code = ''
    request = requests.get(hrefs[i])
    soup = bs4.BeautifulSoup(request.text, 'html.parser')
    flag = -1

    for item in soup.find_all('td'):
        flag += 1
        if len(item.get_text()) > 1 and item.get_text().isnumeric():
            town_code= str(item.get_text())
            town_href = get_href('https://volby.cz/pls/ps2017nss/', str(item.find('a')), 9)
            flag = 0
        if flag == 1:
            town_name = str(item.get_text())
            town_dict[town_name] = [town_code, town_href]
    return town_dict


def write_results(town_dict: dict, file: str) -> None:
    """
    The function write_results goes through the individual towns of the territorial unit and writes the detailed results to the output file.
    First part of file contains the number of registered voters, the number of submitted envelopes, the number of valid votes. 
    Second part contains detailed election result for each election party. Header, first row of final output consists of manually created header and list of electrion parties.
    :param town_dict: dictionary {Town name : [code, link to the detailed election results]}
    :param file: output file
    """
    csv_header = ['Code', 'Location', 'Registered', 'Envelopes', 'Valid']
    csv_output = list()
    outfile = open(file, 'w', encoding='UTF8', newline='')
    writer = csv.writer(outfile, delimiter=";")


    def aux_table_1(parse_table: bs4.element.ResultSet) -> list:
        """
        The auxiliary function (to make the code clearer) processes the 1st table from the detailed results of the towns.
        In list results, the first 2 values that are empty and there are skipped.
        :param parse_table: parsed tables from detailed election results of towns
        :return: list contains dictionary, where key is header and value
        """
        headers = [header.text for header in parse_table[0].find_all('th')]
        headers.insert(1, 'Processed')
        headers.insert(2, 'Processed 2')
        rlist = [{headers[i]: cell.text for i, cell in enumerate(row.find_all('td'))}
               for row in parse_table[0].find_all('tr')]
        return rlist
    

    def aux_table_2_3(parse_table: bs4.element.ResultSet) -> list:
        """
        The auxiliary function (to make the code clearer) processes the 2nd and 3rd tables from the detailed results of the towns.
        In list results, the first 2 values that are empty and there are skipped.
        :param parse_table: parsed tables from detailed election results of towns
        :return: list contains for each election party dictionary with detailed results
        """
        rlist = list()
        headers = ['Code', 'Location', 'Sum', 'Sum in %', 'Link']

        for h in range(1, 3):
            rlist.extend([{headers[i]: cell.text for i, cell in enumerate(row.find_all('td'))}
                        for row in parse_table[h].find_all('tr')][2:])
        return rlist


    for i, town in enumerate(town_dict):
        request = requests.get(town_dict[town][1])
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        tables = soup.find_all('table')
        csv_output.clear()
        csv_output = [town_dict[town][0], town]
        results = aux_table_1(tables)
        csv_output.extend([results[2]['Voličiv seznamu'], results[2]['Vydanéobálky'], results[2]['Platnéhlasy']])
        results.clear()
        results = aux_table_2_3(tables)

        if i == 0:
            csv_header.extend([party['Location'] for party in results])
            writer.writerow(csv_header)
        csv_output.extend([party['Sum'] for party in results])
        writer.writerow(csv_output)
        progress_bar = ['.', '..', '...', '....', '.....', '......', '.......', '........', '.........', '..........']
        print(progress_bar[i % 10], end="\r")
    outfile.close()
    print(' ', end='\r')


def election():
    """
    The function election is main function, which:
    1) calls get_cities, which create list of cities and list of hrefs
    2) checks the correctness of input parameters, the script ends error when:
        - 2 parameters were not specified
        - wrong link to the territorial unit was entered
        - an already existing file was specified
    * Otherwise, the function continues
    3) calls get_towns, which prepares a list of town for a given territorial unit and links to detailed election results
    4) calls write_results, which reads the detailed election results for the town and writes them to the output file,
    :argv 1: input parameter - specific link to the territorial unit
    :argv 2: input parameter - name of output file
    """
    get_cities()
    if len(sys.argv) == 3:
        try:
            inx = hrefs.index(sys.argv[1])
        except ValueError:
            print('Neexistující územní celek ' + '"' + sys.argv[1] + '"!')
            return
        if sys.argv[2] in os.listdir():
            print('Zadaný soubor "' + sys.argv[2] + '" již existuje!')
            return
    else:
        print('Špatný počet argumentů. Dva jsou očekávány!')
        return
    dtowns = get_towns(inx)
    write_results(dtowns, sys.argv[2])


if __name__ == '__main__':
    election()