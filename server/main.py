import time
import BaseHTTPServer

from urlparse import urlparse
import os
import datetime
import json

HOST_NAME = '140.113.86.149' # !!!REMEMBER TO CHANGE THIS!!!i
PORT_NUMBER = 50807 # Maybe set this to 9000.


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""

        tmp = s.path.split('=')
        if len(tmp) == 2 and tmp[0] == '/mday':
            input_time = time.mktime(datetime.datetime.strptime(tmp[1], "%Y%m%d%H%M").timetuple())
            output_data = {}
            tx_data_type = ['lat', 'lng', 'sbi', 'bemp', 'act']
            target_file = ""
            min_diff = float("inf")
            
            my_path = './ubike_dataset/'
            dir_walk = os.walk(my_path).next()
            for filename in dir_walk[2]:
                file_time = time.mktime(datetime.datetime.strptime(filename, "%Y%m%d%H%M%S").timetuple())
                diff = abs(file_time - input_time)
                if diff < min_diff:
                    min_diff = diff
                    target_file = filename

            with open(my_path+target_file) as json_data:
                data = json.load(json_data)
                for sno in data['retVal']:
                    pack = {}
                    for tx_type in tx_data_type:
                        pack[tx_type] = data['retVal'][sno][tx_type]
                    if data['retVal'][sno]['act'] == '0':
                        pack['rate'] = -1
                    else :
                        pack['rate'] = float(data['retVal'][sno]['sbi']) / ( float(data['retVal'][sno]['sbi']) + float(data['retVal'][sno]['bemp']) )
                    output_data[sno] = pack
                    # output_data[sno]['lng'] = data['retVal'][sno]['lng']

            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps(output_data, file, indent=4))

        elif len(tmp) == 2 and tmp[0] == '/sno':
            my_path = './ubike_dataset/'
            dir_walk = os.walk(my_path).next()
            output_data = {}

            for filename in dir_walk[2]:
                pack = {}
                with open(my_path+filename) as json_data:
                    data = json.load(json_data)
                    mday = data['retVal'][tmp[1]]['mday']
                    pack['bemp'] = data['retVal'][tmp[1]]['bemp']
                    pack['sbi'] = data['retVal'][tmp[1]]['sbi']
                    pack['act'] = data['retVal'][tmp[1]]['act']
                output_data[mday] = pack

            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps(output_data, file, indent=4))
        else :
            print 'else'
            
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write("<html><head><title>Title goes here.</title></head>")
            s.wfile.write("<body><p>This is a test.</p>")
            # If someone went to "http://something.somewhere.net/foo/bar/",
            # then s.path equals "/foo/bar/".
            s.wfile.write("<p>You accessed path: %s</p>" % s.path)
            s.wfile.write("</body></html>")
            

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
