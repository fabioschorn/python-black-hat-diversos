import socket

target_host = "172.0.0.1"
target_port = 9997

# Criando um objeto socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviando alguns dados
client.sendto(b"AAABBBCCC", (target_host, target_port))

# Recebendo alguns dados
data, addr = client.recvfrom(4096)

print (data.decode())
client.close()