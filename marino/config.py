# import os

class Config(object):
    MONGO_URI = "mongodb+srv://quest-cluster.rdm3o.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509"
    MONGO_CERT_PATH = "./secrets/X509-cert-8316495671987192482.pem"
    MONGO_DB_NAME = 'exampledb'

    COOKIE_NAME = 'session'
    COOKIE_ENCRYPTION_KEY = "Pc1SRyT6IyDT+KrSE0h4erY5fWZ0kzg5iWDv66jmHFI="

    START_TIME = "2024-11-07 00:40:00"