import os
import platform
import socket
import struct
import sys
import time

ICMP_ECHO_REQUEST = 8  # Código para el tipo de solicitud de eco ICMP

def calculate_checksum(packet):
    # Calcula el checksum de un paquete ICMP
    checksum = 0
    count_to = (len(packet) // 2) * 2

    for i in range(0, count_to, 2):
        checksum += (packet[i + 1] << 8) + packet[i]

    if count_to < len(packet):
        checksum += packet[len(packet) - 1]

    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    return ~checksum & 0xffff

def send_ping_request(dest_addr):
    # Envía una solicitud de eco ICMP al host de destino
    icmp_header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, 0, 1)
    checksum = calculate_checksum(icmp_header)

    icmp_header_with_checksum = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, checksum, 0, 1)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.sendto(icmp_header_with_checksum, (dest_addr, 1))
            send_time = time.time()
            return send_time
    except socket.error as e:
        print("Error al enviar el ping:", e)
        sys.exit()

def receive_ping_reply(sock, send_time):
    # Recibe una respuesta de eco ICMP del host de destino
    timeout = 4  # Espera máximo de 4 segundos para recibir una respuesta

    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            receive_time = time.time()
            packet_data, addr = sock.recvfrom(1024)
            icmp_header = packet_data[20:28]
            type_, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)
            if type_ == 0 and packet_id == os.getpid():
                round_trip_time = receive_time - send_time
                return round_trip_time
        else:
            return None

# Uso del script
host = input("Ingrese el host para hacer ping: ")
send_time = send_ping_request(host)

if send_time is not None:
    print(f"{host} está respondiendo al ping.")
    print(f"Tiempo de ida y vuelta: {send_time:.3f} segundos.")
else:
    print(f"{host} no está respondiendo al ping.")
