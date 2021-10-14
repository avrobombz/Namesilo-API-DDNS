# Namesilo-API-DDNS
DDNS with Namesilo via API

Script pulls records from namesilo, and stores them in DB
Continually monitors external IP address, and when IP changes system updates namesilo with new IP via API and removes old records from SQL database.

pip libraries required:
pip install wasabi
