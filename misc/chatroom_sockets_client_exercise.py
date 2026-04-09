#!/usr/bin/env python
# encoding: utf8
#
# Copyright © Ruben Ruiz Torrubiano <ruben.ruiz at fh-krems dot ac dot at>,
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. Neither the name of the owner nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import zmq
import zmq.asyncio
import pickle
import asyncio
import aioconsole
import sys

context = zmq.asyncio.Context()
req_socket = context.socket(zmq.REQ)
sub_socket = context.socket(zmq.SUB)


def connect():
    """
    Starts the connections.
    :return:
    """
    req_socket.connect("tcp://localhost:7600")
    sub_socket.connect("tcp://localhost:7601")


def subscribe(channel):
    """
    Subscribes to a given channel.
    :param channel:
    :return:
    """
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, channel)


# Task 1: listen asynchronously on the SUB socket and print messages as they arrive
async def message_listener():
    """
    Listens asynchronously on the SUB socket and prints incoming messages.
    :return:
    """
    while True:
        received_message = await sub_socket.recv_string()
        print(f'\nReceived message: {received_message}')


async def message_input(username):
    """
    Performs user input processing.
    :return:
    """
    while True:
        channel = await aioconsole.ainput("Which user do you want to send a message to? (empty = all users, q = quit) ")
        if channel == 'q':
            # Task 3: notify server before disconnecting so it forgets the user
            disconnect_msg = {'type': 'disconnect', 'username': username}
            await req_socket.send(pickle.dumps(disconnect_msg))
            ack = await req_socket.recv_string()
            print(f'Server acknowledged disconnect: {ack}')
            break

        if channel == '':
            channel = 'GENERAL'

        content = await aioconsole.ainput("Which message do you want to send? ")
        message = {'type': 'message', 'channel': channel, 'content': content}
        await req_socket.send(pickle.dumps(message))

        # Task 2: check acknowledgement from server (REQ/REP)
        ack = await req_socket.recv_string()
        print(f'Server acknowledged: {ack}')


async def main(username):
    # Task 3: send login request and check for existing session
    login_msg = {'type': 'login', 'username': username}
    await req_socket.send(pickle.dumps(login_msg))
    response = await req_socket.recv_string()
    if response == 'ERR':
        print(f'Username "{username}" is already in use. Disconnecting.')
        return
    print(f'Logged in as "{username}" (server response: {response})')

    # Task 1: run listener and input loop concurrently
    listener_task = asyncio.create_task(message_listener())
    await message_input(username)
    listener_task.cancel()


if __name__ == "__main__":
    connect()
    subscribe('GENERAL')
    username = sys.argv[1] if len(sys.argv) > 1 else 'anonymous'
    subscribe(username)
    print("Client started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(username))
    req_socket.close()