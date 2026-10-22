"""Reject ambiguous response JSON with real loopback HTTP; no external API."""
import json, threading, unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from jev_pii.client import TypeSafeTransport
from jev_pii.i18n import PiiError
from test_live import response

class DuplicateResponseTests(unittest.TestCase):
    def test_duplicate_members_at_every_level_and_nonfinite_json_fail_closed(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200);self.end_headers();self.wfile.write(self.server.body)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            client=TypeSafeTransport('synthetic',endpoint=f'http://127.0.0.1:{server.server_port}/v1/systemone',allow_loopback=True)
            valid=json.dumps(response(),separators=(',',':'))
            server.body=valid.encode();self.assertEqual(client.send(b'{}')['category'],'other')
            malformed=[
                valid.replace('"model":"jev-1.13.0"','"model":"PRIVATE_SENTINEL","model":"jev-1.13.0"'),
                valid.replace('"choice":"other"','"choice":"PRIVATE_SENTINEL","choice":"other"',1),
                valid.replace('"input_tokens":123','"input_tokens":99,"input_tokens":123'),
                valid[:-1]+',"extra":NaN}',valid[:-1]+',"extra":Infinity}',valid[:-1]+',"extra":-Infinity}',
            ]
            for raw in malformed:
                server.body=raw.encode()
                with self.subTest(raw=raw):
                    with self.assertRaises(PiiError) as error:client.send(b'{}')
                    self.assertEqual(error.exception.code,'response')
                    self.assertNotIn('PRIVATE_SENTINEL',str(error.exception))
        finally:server.shutdown();server.server_close();thread.join()
