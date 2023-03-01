#!/bin/bash

APP_PREFIX=/app/wireguard
WG_ID=wg0

WG_PREFIX="/etc/wireguard"
WG_KEYS_PREFIX="${WG_PREFIX}/data"
WG_PRIVKEY_FILE="${WG_KEYS_PREFIX}/priv.key"
WG_PUBKEY_FILE="${WG_KEYS_PREFIX}/pub.key"


# turn on bash's job control
set -m


init_db() {
    python3 "${APP_PREFIX}/manager.py" initialize_database || true
}

generate_privkey_if_not_exists() {
    if [ ! -r "${WG_PRIVKEY_FILE}" ]; then
        wg genkey > "${WG_PRIVKEY_FILE}"
    fi
}
calculate_pubkey() {
    cat "${WG_PRIVKEY_FILE}" | wg pubkey > "${WG_PUBKEY_FILE}"
}

generate_server_config() {
    python3 "${APP_PREFIX}/manager.py" generate_config || exit
}

run_wireguard_server() {
    wg-quick up "${WG_ID}"
}

run_manager() {
    python3 "${APP_PREFIX}/manager.py" run
}


init_all() {
    init_db
    generate_privkey_if_not_exists
    calculate_pubkey
    generate_server_config
}

run() {
    run_wireguard_server &
    run_manager
}

init_all
run


