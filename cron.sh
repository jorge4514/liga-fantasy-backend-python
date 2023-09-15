#!/bin/bash

# Contenido del script.sh para ejecutar cada 4 horas
(crontab -l ; echo "0 */4 * * * ./fantasy_scraper.py") | crontab -
