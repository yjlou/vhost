#!/usr/bin/python3

# This is the host and port for this virtual host server to listen.
#
VHOST_HOST = '0.0.0.0'
VHOST_PORT = 80

# This is the mapping table for each virtual host.
#
# The key is the 'Host:' header we receive from browser. All in lower case.
# The value is the host and port we are going to forward to.
#
MAPPING = {
  'your_virtualhost_1.com': ('localhost', 5566),
  'your_virtualhost_2.com': ('another_host', 7788),
  'your_virtualhost_3.com': ('192.168.1.1', 183),
}

# When there is no match in MAPPING table, forward request to this server.
DEFAULT_HOST = 'google.com'
DEFAULT_PORT = 80
