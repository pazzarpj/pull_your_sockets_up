###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from queue import Queue, Empty
import threading
import asyncio
import sys


q = Queue()


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.sendMessage(u"Hello, world!".encode('utf8'))
        self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
        self.check_queue()

    def check_queue(self):
        global q
        try:
            msg = q.get_nowait()
            #msg = yield from q.get_nowait()
        except Empty:
            pass
        else:
            self.sendMessage(msg.encode('utf8'))
        self.factory.loop.call_later(0.010, self.check_queue)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


def run_async_loop(loop, coro):
    try:
        while True:
            loop.run_until_complete(coro)
    finally:
        loop.close()


@asyncio.coroutine
def read_input():
    while True:
        if not sys.stdin.isatty():
            for line in sys.stdin:
                print('.')
                q.put(line)
                yield
        else:
            print('.')
            yield

def read_file():
    with open(r"C:\Users\dave_000\Downloads\richmondrowingclub.wordpress.2015-05-12.xml") as f:
        for line in f.readline():
            print('.')
            q.put(line)


def print_forever():
    while True:
        print('.'.join(['',sys.stdin.read()]))

if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketClientFactory("ws://localhost:9000", debug=False)
    factory.protocol = MyClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, 'localhost', 9000)
    my_proto = loop.run_until_complete(coro)
    loop.call_soon(read_file())
    try:
        loop.run_forever()
    finally:
        loop.close()