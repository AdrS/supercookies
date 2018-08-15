#!/usr/bin/env python3
import http.server
import socketserver
import sys

uid = 0

class Handler(http.server.SimpleHTTPRequestHandler):
	def _get_index(self, prefix):
		s = self.path[len(prefix):]
		if not s.isdigit():
			self.send_response(404)
			self.send_header('content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(b'404')
		return int(s)
		
	def do_GET(self):
		global uid
		# Client makes request here to tell server its id
		if self.path.startswith('/setbits'):
			uid = self._get_index('/setbits')
			self.send_response(200)
			self.send_header('content-type', 'text/plain')
			self.send_header('content-length', '0')
			self.end_headers()
		elif self.path.startswith('/testbit'):
			idx = self._get_index('/testbit')
			# Server issues perminant redirects for client to cache
			# This causes client to store id encoded as:
			# redirected = 1, not redirected = 0
			if (uid >> idx) & 1 == 1:
				self.send_response(301)
				self.send_header('content-type', 'text/plain')
				self.send_header('content-length', '0')
				self.send_header('location', 'http://localhost:8080/onebit%d' % idx)
				self.end_headers()
			else:
				self.send_response(200)
				self.send_header('content-type', 'text/plain')
				self.send_header('content-length', '1')
				self.end_headers()
				self.wfile.write(b'0')
		elif self.path.startswith('/onebit'):
			self.send_response(200)
			self.send_header('content-type', 'text/plain')
			self.send_header('content-length', '1')
			self.end_headers()
			self.wfile.write(b'1')
		else:
			http.server.SimpleHTTPRequestHandler.do_GET(self)

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
	pass

if __name__ == '__main__':
	port = 8080
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	if len(sys.argv) > 2 or port <= 0 or port >= (1<<16):
		print('usage: %s [port]' % sys.argv[0], file=sys.stderr)
		sys.exit(1)

	server = Server(('localhost', port), Handler)
	server.serve_forever()
