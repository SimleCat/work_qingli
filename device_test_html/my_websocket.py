# _*_ coding:utf-8 _*_
import re
import socket
import base64
import hashlib
import struct

HOST = ''
PORT = 8888
BUF_SIZE = 1024
LISTEN_NUM = 5
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING =  "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade:websocket\r\n" \
                    "Connection: Upgrade\r\n" \
                    "Sec-WebSocket-Accept: %s\r\n" \
                    "WebSocket-Location: ws://%s/chat\r\n" \
                    "WebSocket-Protocol:chat\r\n\r\n"
# HANDSHAKE_STRING =  "HTTP/1.1 101 Switching Protocols\r\n" \
#                     "Upgrade:websocket\r\n" \
#                     "Connection: Upgrade\r\n" \
#                     "Sec-WebSocket-Accept: %s\r\n"

patt_webkey = re.compile(r'Sec-WebSocket-Key: (.+)\r')

def handshake(conn):
    headers = {}
    shake = conn.recv(BUF_SIZE)

    print "Recive:"
    print shake

    if not len(shake):
        return False

    tmp = re.findall(patt_webkey, shake)
    if not tmp:
        print ('This socket is not websocket, client close.')
        return False

    sec_key = tmp[0]
    res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

    # str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ':' + str(PORT))
    str_handshake = HANDSHAKE_STRING % (res_key, '%s:%s' % (HOST, str(PORT)))
    # str_handshake = HANDSHAKE_STRING % res_key
    print "Send:"
    print str_handshake
    conn.send(str_handshake)

    return True


def send_data(conn, data):
    if data:
        data = str(data)
    else:
        return False
    token = "\x81"
    length = len(data)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    data = '%s%s' % (token, data)
    conn.send(data)
    return True



def recv_data(conn):
    try:
        all_data = conn.recv(BUF_SIZE)
        print 'Recive:'
        print all_data
        if all_data == False:
            return False
        if not len(all_data):
            return None
    except:
        return False
    else:
        code_len = ord(all_data[1]) & 127
    if code_len == 126:
        masks = all_data[4:8]
        data = all_data[8:]
    elif code_len == 127:
        masks = all_data[10:14]
        data = all_data[14:]
    else:
        masks = all_data[2:6]
        data = all_data[6:]
    raw_str = ""
    i = 0
    for d in data:
        raw_str += chr(ord(d) ^ ord(masks[i % 4]))
        i += 1
    return raw_str





# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# try:
#     sock.bind((HOST, PORT))
#     print "Bind %s, ready to use" % PORT
# except:
#     print("Port[%s] is already uesed, quit" % PORT)
#     exit(1)

# sock.listen(LISTEN_NUM)

# conn, addr = sock.accept()
# # shake = conn.recv(BUF_SIZE)
# # print shake
# # print repr(shake)
# if handshake(conn):
#     print 'Handshake success'
# else:
#     print 'Handshake failure'

# all_data = recv_data(conn)
# print 'Recive:'
# print repr(all_data)
# all_data = recv_data(conn)
# print 'Recive:'
# print repr(all_data)

# all_data = recv_data(conn)
# print 'Recive:'
# print repr(all_data)

# conn, addr = sock.accept()
# if handshake(conn):
#     print 'Handshake success'
# else:
#     print 'Handshake failure'

# conn.close()
# sock.close()