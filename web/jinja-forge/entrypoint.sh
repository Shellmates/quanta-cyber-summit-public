#!/bin/sh
# Écrire le flag dans un fichier pour que l'exploit SSTI puisse le lire
echo "${FLAG}" > /app/flag 2>/dev/null || true
exec python app.py
