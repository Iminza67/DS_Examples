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
#

import grpc
import example_pb2
import example_pb2_grpc

if __name__ == '__main__':
    with grpc.insecure_channel('grpc-server:50051') as channel:
        stub = example_pb2_grpc.CustomerServiceStub(channel)
        customer0 = example_pb2.Customer(forename='John', surname='Smith')

        response = stub.AddCustomer(customer0)
        print(f'First request response = {response.success}')
        response2 = stub.AddCustomer(example_pb2.Customer(forename='Tina', surname='A.'))
        print(f'Second request response = {response2.success}')

        if response.success:
            # add purchases for Smith — Task 1: iterate the stream of PurchaseResults
            purchase1 = example_pb2.Purchase(purchase_id=0, customer_id=response.customers[0].id, total_price=100.0,
                                             articles=[1, 2, 3])
            purchase2 = example_pb2.Purchase(purchase_id=0, customer_id=response.customers[0].id, total_price=50.0,
                                             articles=[5])
            # purchase for a non-existent customer to demo the error path
            purchase3 = example_pb2.Purchase(purchase_id=999, customer_id=999, total_price=20.0)

            for result in stub.SendPurchases(p for p in [purchase1, purchase2, purchase3]):
                if result.success:
                    print(f'Purchase {result.purchase_id} for customer {response.customers[0].id} added successfully')
                else:
                    print(f'Purchase {result.purchase_id} failed: {result.error_message}')