etuovi apartments scraper
================================

Main file: ``etuovi_apartments_scraper.py``

Webscraper for etuovi.fi apartment listings

To edit apartment search change these values below (Line 168)

LINE 168: ``search = apartments_webscraper('City', 'max price', 'min price', 'max size', 'min size')`` 

Data output
------------

Data output is saved to Excel file that begins with city name and ends with current timestamp
e.g. ``Rovaniemi_apartment_search_2020-04-18 13:58.xlsx`` See example file in repository.

Data output is also printed in terminal

Data visualization
------------

For each execution three histogram/bar plot figures are created  
![Alt text](/doc/Figure_1.png?raw=true "Data visualization1")

![Alt text](/doc/Figure_2.png?raw=true "Data visualization2")

![Alt text](/doc/Figure_3.png?raw=true "Data visualization3")
