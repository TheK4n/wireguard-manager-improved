FROM python:3.10-slim

ENV WG_PORT=51830 APP_PREFIX=/app/wireguard
EXPOSE ${WG_PORT}/udp
WORKDIR ${APP_PREFIX}

RUN apt update -y && apt install -y wireguard wireguard-dkms wireguard-tools iproute2 iptables 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY . .

CMD ["bash", "initializer.sh"]

