from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from chirpstack_api.as_pb.external import api
from google.protobuf.json_format import Parse
import requests
import grpc
import json
import sys

server = "host.docker.internal:8080"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTY0NjI2NjIwNywiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjQ2MTc5ODA3LCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.MjtDxqKb12DPol4GRkqdoT281tAlN4nbl4jslI-D4G4"

def downlink(body, dev_eui):
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

        # Print the downlink frame-counter value.
        print(resp.f_cnt)

def logmein(user, passwd):
        url = 'http://host.docker.internal:8080/api/internal/login'
        creds = "{ \"email\": \"" +  user + "\", \"password\": \"" + passwd + "\"}"

        x = requests.post(url, data = creds)
        j = json.loads(x.text)
        return j["jwt"]

api_token = logmein('admin', 'admin')

def main():
        argstr = ""
        argcnt = len(sys.argv)
        for arg in range(1, argcnt):
                nextarg = sys.argv[arg:arg+1]
                print(nextarg)
                argstr = argstr + ' ' + nextarg[0]
        print("Sending %s" % (argstr))
        downlink(argstr.encode(), "DDEEAADDBBEEEEFF")

if __name__ == "__main__":
    main()

