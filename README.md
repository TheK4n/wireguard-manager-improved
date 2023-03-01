
<h1 align="center">WireguardManagerImproved</h1>


<p align="center">
  <a href="https://github.com/TheK4n">
    <img src="https://img.shields.io/github/followers/TheK4n?label=Follow&style=social">
  </a>
  <a href="https://github.com/TheK4n/wireguard-manager-improved">
    <img src="https://img.shields.io/github/stars/TheK4n/wireguard-manager-improved?style=social">
  </a>
</p>


* [Project description](#chapter-0)
* [Installation](#chapter-1)
* [Usage](#chapter-2)


<a id="chapter-0"></a>
## Project description
Next generation of <a href="https://github.com/thek4n/wireguard-manager">wireguard-manager</a>
\
Wireguard server with telegram integration in docker containers with a client manager providing external API that allows you to add/remove vpn clients and resume/suspend their access

<p align="center">
<a href="#">
    <img align="center" width="380" src=".assets/preview.gif">
</a>
<a id="chapter-1"></a>



<a id="chapter-1"></a>
## Installation

1. Pull project
```bash
git clone https://github.com/TheK4n/wireguard-manager-improved && \
cd wireguard-manager-improved
```

2. Write variables to `.env` file
```env
TG_BOT_TOKEN=0000000000000:7PIThN8LmYBs7wkoQ9Z6ts08R3JO+Tu/ZQL9AqyJa3/  # telegram bot token
TG_BOT_ADMINS=00000001,00000002  # telegram ids of admins, separated by comma

POSTGRES_USER=postgres
POSTGRES_DATABASE_NAME=postgres
POSTGRES_PASSWORD=mhYInZYRaWZy3q+ifD7qkQ  # set a secure password via `openssl rand -base64 16`
```

3. Run project
```bash
docker-compose up -d
```


<a id="chapter-2"></a>
## Usage

* `./api.sh create <username>` - Create client with username
* `./api.sh get <username>` - Get client vpn config
* `./api.sh qr <username>` - Get qrcode of client vpn config
* `./api.sh delete <username>` - Delete client with username


Api documentation you can find in [docs](docs)
