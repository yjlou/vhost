#!/usr/bin/python3

import socket
import socketserver

import conf

# For debug
def PRINT(s):
  if True:
    print(s)


class MyTCPHandler(socketserver.StreamRequestHandler):
  def handle(self):
    lines = []
    host, port = None, None
    while self.rfile:
      line = self.rfile.readline()
      PRINT(line)
      lines.append(line)

      text = line.decode('utf-8').strip()
      if text.startswith('Host: '):
        # Host: sad5566.com:5665
        host_port = text.split(' ')[1].split(':')
        if len(host_port) > 1:
          host, port = host_port
        else:
          host = host_port[0]
          port = 80
        break

    forward = conf.MAPPING.get(host.lower())
    if forward:
      host, port = forward
    else:
      host, port = conf.DEFAULT_HOST, conf.DEFAULT_PORT

    PRINT('Forward to {}:{}'.format(host, port))

    # Connect to the real server.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # First send whatever we got from the client.
    for line in lines:
      PRINT(line)
      sock.send(line)

    while self.rfile:
      line = self.rfile.readline()
      PRINT(line)
      sock.send(line)
      if line == b'\r\n':
        break

    while True:
      chunk = sock.recv(1024)
      PRINT(chunk)
      if chunk == b'':
        break
      self.wfile.write(chunk)


if __name__ == "__main__":

  # Create the server, binding to localhost on port 9999
  socketserver.TCPServer.allow_reuse_address = True
  server = socketserver.TCPServer((conf.VHOST_HOST, conf.VHOST_PORT), MyTCPHandler)
  print('Listening on {}:{} ...'.format(conf.VHOST_HOST, conf.VHOST_PORT))

  # Activate the server; this will keep running until you
  # interrupt the program with Ctrl-C
  server.serve_forever()
