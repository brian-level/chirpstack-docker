from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from chirpstack_api.as_pb import integration
from chirpstack_api.as_pb.external import api
from google.protobuf.json_format import Parse
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import socket
import requests
import grpc
import os
import json

server = "host.docker.internal:8080"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTY0NjM1OTIyMywiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjQ2MjcyODIzLCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.ychMhAulVeYmKn2Ap02fEjA8E_G9aYl_m8qx7RjoCBE"

class Handler(BaseHTTPRequestHandler):
    # True -  JSON marshaler
    # False - Protobuf marshaler (binary)
    json = False
    pings = 0
    pongs = 0

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        query_args = parse_qs(urlparse(self.path).query)

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        if query_args["event"][0] == "up":
            self.pings+= 1
            self.up(body)

        elif query_args["event"][0] == "join":
            self.join(body)

        elif query_args["event"][0] == "txack":
            self.pongs+= 1

        else:
            print("handler for event %s is not implemented" % query_args["event"][0])

    def up(self, body):
        up = self.unmarshal(body, integration.UplinkEvent())
        print("Uplink received frame %d from: %s with payload: %s" % (up.f_cnt, up.dev_eui.hex(), up.data.hex()))

        # "PNG%02X%03X%03X", mCurrentTestID, mCurrentTestCycle, paylen
        testid = int('0x' + chr(up.data[3]) + chr(up.data[4]), base=16)
        cycle  = int('0x' + chr(up.data[5]) + chr(up.data[6]) + chr(up.data[7]), base=16)

        print("Test ID: %d  Cycle: %d" % (testid, cycle))

        # send packet back as pong
        self.bg_downlink(up.data, up.dev_eui.hex())

    def join(self, body):
        join = self.unmarshal(body, integration.JoinEvent())
        print("Device: %s joined with DevAddr: %s" % (join.dev_eui.hex(), join.dev_addr.hex()))

    def unmarshal(self, body, pl):
        if self.json:
            return Parse(body, pl)

        pl.ParseFromString(body)
        return pl

    def bg_downlink(self, body, dev_eui):
        #os.system("python3 dl.py")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.downlink(body, dev_eui))

    def downlink(self, body, dev_eui):
        # need to give embedded radio time to turn around to Rx
        sleep(0.2)

        # Connect without using TLS.
        channel = grpc.insecure_channel(server)

        # Device-queue API client.
        client = api.DeviceQueueServiceStub(channel)

        # Define the API key meta-data.
        auth_token = [("authorization", "Bearer %s" % api_token)]

        # Construct request.
        req = api.EnqueueDeviceQueueItemRequest()
        req.device_queue_item.confirmed = False
        req.device_queue_item.data = body
        req.device_queue_item.dev_eui = dev_eui
        req.device_queue_item.f_port = 1

        resp = client.Enqueue(req, metadata=auth_token)

        print("Downlink replied frame %d eui=%s %d bytes data=%s" % (resp.f_cnt, dev_eui, len(body), body.hex()))

def isOpen(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1000)
        try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

def checkHost(ip, port):
        ipup = False
        for i in range(30):
                if isOpen(ip, port):
                        ipup = True
                        break
                else:
                        sleep(1)
        return ipup

def logmein(user, passwd):
        #url = 'http://localhost:8080/api/internal/login'
        url = 'http://host.docker.internal:8080/api/internal/login'
        creds = "{ \"email\": \"" +  user + "\", \"password\": \"" + passwd + "\"}"

        hostname = "host.docker.internal"

        if checkHost(hostname, 8090):
                  print ("App server host " + hostname + " is up ")

        x = requests.post(url, data = creds)
        j = json.loads(x.text)
        return j["jwt"]

api_token = logmein('admin', 'admin')
httpd = HTTPServer(('', 8090), Handler)
httpd.serve_forever()

