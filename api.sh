#!/bin/sh


base_request() {
curl -X "$1" \
    "http://127.0.0.1:8080/clients/$2" \
    -H 'Accept: plain/text, application/json' \
    -H 'Content-Type: application/json' \
    -Ls \
    -d "{\"username\": \"$3\"}"
}


GET() {
    base_request GET "$1"
}

QR() {
    base_request GET "$1" | qrencode -t ansiutf8 -l L
}

POST() {
    base_request POST "" "$1"
}

DELETE() {
    base_request DELETE "$1"
}

OPTIONS() {
    base_request OPTIONS
}
    
    
case "$1" in
    get) shift;    GET "$@" ;;
    qr) shift;     QR "$@" ;;
    create) shift;   POST "$@" ;;
    delete) shift; DELETE "$@" ;;
esac
exit 0
