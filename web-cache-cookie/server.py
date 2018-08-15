#!/usr/bin/env python3
import http.server
import socketserver
import sys
import time

uid = 0
uid_birth = 0

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
		global uid_birth
		print(uid)

		# Associate uid with client for 30 seconds (server
		# uses proper cache control headers while the client
		# causes the browser to cache proper pages)
		if time.time() > uid_birth + 30:
			print('Forgetting client')
			uid = 0

		# Client makes request here to tell server its id
		if self.path.startswith('/setbits'):
			uid = self._get_index('/setbits')
			uid_birth = time.time()
			self.send_response(200)
			self.send_header('content-type', 'text/plain')
			self.send_header('content-length', '0')
			self.end_headers()
		elif self.path.startswith('/testbit'):
			idx = self._get_index('/testbit')
			# Add artificial delay to make timing difference between
			# Cached and not cached more pronounced
			time.sleep(1)

			self.send_response(200)
			# Server tells client to cache response
			# This causes client to store id encoded as:
			# cached = 1, not cached = 0
			if (uid >> idx) & 1 == 1:
				print('Setting cache control for /testbit%d' % idx)
				self.send_header('cache-control', 'max-age=31536000')

			self.send_header('content-type', 'text/plain')
			self.send_header('content-length', '0')
			self.end_headers()
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
