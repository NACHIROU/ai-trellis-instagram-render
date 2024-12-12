# Environment variables
# Create a copy of this file and rename it to `.env`

# Basic
APP_ENV="DEV"
APP_SETTINGS_LOG_DIR="/tmp/"
APP_SETTINGS_CRYPTO_SECRET="xxx-xxxxxxxxx-xxxxxx"
APP_SETTINGS_THEME_COFFEE_CDN="https://theme-coffee-staging.vercel.app"

# MongoDB
APP_SETTINGS_MONGO__PROTOCOL="mongodb+srv"
APP_SETTINGS_MONGO__HOST="cluster0.thwi2yv.mongodb.net"
APP_SETTINGS_MONGO__DB="trellix-instagram"
APP_SETTINGS_MONGO__USERNAME="somadnachirou"
APP_SETTINGS_MONGO__PASSWORD="Passw0rde"
APP_SETTINGS_MONGO__PARAMS="retryWrites=true&w=majority"
APP_SETTINGS_MONGO__PORT=""

# SSL
APP_SETTINGS_SSL_KEYFILE="./localhost-key.pem"
APP_SETTINGS_SSL_CERTFILE="./localhost.pem"

# Trellis Instagram
APP_SETTINGS_INSTAGRAM__BEANS_PUBLIC="tls_public_0v53rm"
APP_SETTINGS_INSTAGRAM__BEANS_SECRET="tls_secret_0ploczdsxrd1z4y59a3ol8hr48myodlk"
APP_SETTINGS_INSTAGRAM__THIRD_PARTY_PUBLIC="611793904486901"
APP_SETTINGS_INSTAGRAM__THIRD_PARTY_SECRET="f633a6b9422263d1498a8f354683ac78"
APP_SETTINGS_INSTAGRAM__APP_DOMAIN="https://localhost/"


# ################################# #
# TESTCASES                         #
# ################################# #

# Merchant identifiers
# To retrieve the merchant identifiers visit: https://trellis.trybeans.com/tokenify
APP_SETTINGS_TESTCASES__BEANS_CARD_ID="card_0b6z1z7q"
APP_SETTINGS_TESTCASES__BEANS_CARD_ADDRESS="$xxxxxxx"
APP_SETTINGS_TESTCASES__BEANS_ACCESS_TOKEN="sk_0e1wp03isb3iuc3chnali0gh49jmkj3h28933"

# Shopper identifiers
# To retrieve a shopper identifier, just add a new member: https://help.trybeans.com/members/add-members
APP_SETTINGS_TESTCASES__BEANS_MEMBER_1_ID="acc_xxxxxxxxxxxxx"
APP_SETTINGS_TESTCASES__BEANS_MEMBER_1_EMAIL="xxxxx@example.com"
