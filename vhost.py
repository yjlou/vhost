#!/usr/bin/python3

import resource
import socket
import socketserver
import threading

import conf

# For debug
def PRINT(s):
  if True:
    print(s)


class MyTCPHandler(socketserver.StreamRequestHandler):
  def handle(self):
    lines = []
    host, port = None, None
    first_line = True
    found_get_my_client_ip = False

    while self.rfile:
      line = self.rfile.readline()
      if not line:  # EOF
        break

      PRINT(line)
      lines.append(line)

      # end of headers
      if line == b'\r\n':
        break

      text = line.decode('utf-8').strip()

      # Parse for special command
      if first_line:
        first_line = False
        if 'GET /get_my_client_ip' in text:
          found_get_my_client_ip = True

      if text.startswith('Host: '):
        # Host: sad5566.com:5665
        host_port = text.split(' ')[1].split(':')
        if len(host_port) > 1:
          host, port = host_port
        else:
          host = host_port[0]
          port = 80
        break

    if host is not None:
      forward = conf.MAPPING.get(host.lower())
    else:
      forward = None

    if forward:
      host, port = forward
    else:
      host, port = conf.DEFAULT_HOST, conf.DEFAULT_PORT

    client_addr = self.client_address[0]

    if found_get_my_client_ip:
      output = 'HTTP/1.0 200 OK\r\n\r\n{}'.format(client_addr)
      self.wfile.write(output.encode('utf-8'))
      return

    PRINT('Forward {} to {}:{}'.format(client_addr, host, port))

    # Connect to the real server.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # First send whatever we got from the client.
    for line in lines:
      PRINT(line)
      sock.send(line)

    while self.rfile:
      line = self.rfile.readline()
      if not line:  # EOF
        break

      PRINT(line)
      sock.send(line)
      if line == b'\r\n':
        break

    while True:
      chunk = sock.recv(1024)
      PRINT(chunk)
      if not chunk:
        break
      self.wfile.write(chunk)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
  # To prevent this error: OSError: [Errno 24] Too many open files
  resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

  socketserver.TCPServer.allow_reuse_address = True

  # Create the server, binding to localhost on port 9999
  if True:
    # Multithread
    server = ThreadedTCPServer((conf.VHOST_HOST, conf.VHOST_PORT), MyTCPHandler)
  else:
    # Single thread
    server = socketserver.TCPServer((conf.VHOST_HOST, conf.VHOST_PORT), MyTCPHandler)

  print('Listening on {}:{} ...'.format(conf.VHOST_HOST, conf.VHOST_PORT))

  # Activate the server; this will keep running until you
  # interrupt the program with Ctrl-C
  server.serve_forever()
