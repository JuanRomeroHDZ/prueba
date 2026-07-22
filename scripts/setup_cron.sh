#!/bin/bash

# Obtener directorio absoluto del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/it-market-env/bin/python3"
LOG_FILE="$PROJECT_DIR/cron_scraper.log"

CRON_JOB="0 8 * * * cd $PROJECT_DIR && PYTHONPATH=. $PYTHON_BIN test_scraper.py >>$LOG_FILE 2>&1"

# Verificar si el cron job ya existe
(crontab -l 2>/dev/null | grep -F "$PROJECT_DIR") >/dev/null

if [ $? -eq 0 ]; then
    echo "⚠️ El cron job para IT Market Analyzer MX ya está instalado."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Automatización configurada con éxito en Debian."
    echo "📅 Se ejecutará diariamente a las 8:00 AM."
fi
