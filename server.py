#  coding: utf-8 
import socketserver
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Copyright 2023 Paige Lekach

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class MyWebServer(socketserver.BaseRequestHandler):

    # Function to parse request type and returning 405 if not GET
    def splitGetRequest(self, request):
        req, path, http = request.split(" ")
        if req != "GET":
            return 'HTTP/1.1 405 Method Not Allowed\r\n\r\n', path
        return req, path

    # Determining if handling css or html request, returning corresponding mim-type
    def determineFile(self, path):
        if '.css' in path:
            return 'text/css\r\n'
        return 'text/html\r\n'

    # Opening and reading content of passed in file path, catching paths that don't exist
    def getFileContent(self, path):
        try:
            t = open(path, "r")
            content = ''
            for v in t.readlines():
                content = content + v
            # returning content to add to response
            return content
        except IOError as e:
            # path does not exist
            return 'HTTP/1.1 404 Not FOUND!\r\n'
    
    def handle(self):
        self.data = self.request.recv(1024)

        getRequest= self.data.decode("utf-8").split("\r\n")

        req, path = self.splitGetRequest(getRequest[0])

        # extracting headers from the content sent
        for s in getRequest[1:]:
            if ": " not in s:
                getRequest.remove(s)
        
        # spliting up headers from request
        headersDict = dict(s.split(': ') for s in getRequest[1:])

        # extracting host from headers
        host = headersDict['Host']

        if '405' in req:
            # unsupported request type, send 405 response
            self.request.sendall(bytearray(req, 'utf-8'))
        else:
            # www base path to build on
            basePath = 'www' + path
            # default ok response
            response = 'HTTP/1.1 200 OK\r\nContent-Type: '
            # getting file type and determining content-type to send
            fileType = self.determineFile(basePath)
            # potential file content
            content = ''

            # adding safety fo users can't exit www
            if '../' in basePath:
                basePath = basePath.replace('../', '')
            
            # determining if directory or not
            if basePath.endswith('/'):
                content = self.getFileContent(basePath + 'index.html')
            else:
                content = self.getFileContent(basePath)

            if '404 Not FOUND!' in content:
                # checking if path is to directory
                missingSlash = self.getFileContent(basePath + '/index.html')

                if '404 Not FOUND!' not in missingSlash:
                    # request for directory
                    # no need for www in the location url
                    basePath = basePath.replace("www/", "")
                    response = 'HTTP/1.1 301 Moved Permanently\r\nContent-Type: ' + fileType + 'Location: http://' + host + '/' + basePath + '/' + '\r\n\r\n'

                else:
                    # checking if path is to file without extension
                    missingHTMLExtension = self.getFileContent(basePath + '.html')

                    if '404 Not FOUND!' not in missingHTMLExtension:
                        fileType = self.determineFile(basePath + '.html')
                        response = response + fileType + '\r\n\r\n' + missingHTMLExtension + '\r\n\r\n'
                    else:
                        # path DNE
                        response = content
                
            else:
                response = response + fileType + '\r\n\r\n' + content + '\r\n\r\n'
            
            self.request.sendall(bytearray(response, 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
