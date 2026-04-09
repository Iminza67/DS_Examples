import grpc
import example_pb2
import example_pb2_grpc

if __name__ == '__main__':
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = example_pb2_grpc.CustomerServiceStub(channel)

        # Add two customers
        r1 = stub.AddCustomer(example_pb2.Customer(forename='John', surname='Smith'))
        r2 = stub.AddCustomer(example_pb2.Customer(forename='Tina', surname='A. '))

        # John: 80 + 90 = 170, Tina: 100 + 100 = 200
        purchases = [
            example_pb2.Purchase(purchase_id=0, customer_id=r1.customers[0].id, total_price=80.0),
            example_pb2.Purchase(purchase_id=1, customer_id=r1.customers[0].id, total_price=90.0),
            example_pb2.Purchase(purchase_id=0, customer_id=r2.customers[0].id, total_price=100.0),
            example_pb2.Purchase(purchase_id=1, customer_id=r2.customers[0].id, total_price=100.0),
        ]
        for _ in stub.SendPurchases(p for p in purchases):
            pass  # consume stream

        # Task 2: ask for all customers who spent more than 100€
        threshold = 100.0
        print(f'Customers with total purchases over {threshold}€:')
        for customer in stub.GetHighSpenders(example_pb2.AmountThreshold(min_amount=threshold)):
            total = sum(p.total_price for p in customer.purchases)
            print(f'Customer {customer.id} ({customer.forename} {customer.surname}) total spent: {total}€')