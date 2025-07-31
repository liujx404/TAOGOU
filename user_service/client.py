import grpc
from protos import user_pb2_grpc, user_pb2

def test_create_user(stub):
    try:
        request = user_pb2.CreateUserRequest()
        request.mobile = "18844542344"
        response = stub.CreateUser(request)
        print(response)
    except grpc.RpcError as e:
        print(e.code())
        print(e.details())

def test_get_user_by_id(stub):
    try:
        request = user_pb2.IdRequest()
        request.id = 1950920017818157056
        response = stub.GetUserById(request)
        print(response) 
    except grpc.RpcError as e:
        print(e.code())
        print(e.details())

def test_get_user_by_mobile(stub):
    try:
        request = user_pb2.MobileRequest()
        request.mobile = '18824244'
        response = stub.GetUserByMobile(request)
        print(response) 
    except grpc.RpcError as e:
        print(e.code())
        print(e.details())

def main():
    with grpc.insecure_channel('localhost:5001') as channel:
        stub = user_pb2_grpc.UserStub(channel)
        test_get_user_by_mobile(stub)

if __name__ == '__main__':
    main()