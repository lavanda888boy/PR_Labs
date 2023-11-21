from raft import RAFTFactory
import time
import random

service_info = {
    "host" : "127.0.0.1",
    "port" : 8000
}

time.sleep(random.randint(1,3))

node = RAFTFactory(service_info).create_server()
print(node.leader)