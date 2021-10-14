# Namesilo-API-DDNS
DDNS with Namesilo via API

Script pulls records from namesilo, and stores them in DB
Continually monitors external IP address, and when IP changes script updates namesilo with new IP via API and removes old records from SQL database.
Script pulls its own configuration from SQL, allowing variables to be updated on the fly.

pip libraries required:
pip install wasabi
