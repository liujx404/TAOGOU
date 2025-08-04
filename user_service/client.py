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

def test_update_avatar(stub):
    try:
        request = user_pb2.AvatarRequest()
        request.id = 1950920768128811008
        request.avatar = 'https://www.zlkt.net/xx.jpg'
        response = stub.UpdateUserAvatar(request)
        print(response)
    except grpc.RpcError as e:
        print(e.code())
        print(e.details())

def test_update_usernmae(stub):
    try:
        request = user_pb2.UsernameRequest()
        request.id = 1950920768128811008
        request.username = '水獭222'
        response = stub.UpdateUsername(request)
        print(response)
    except grpc.RpcError as e:
        print(e.code())

def test_update_password(stub):
    try:
        request = user_pb2.PasswordRequest()
        request.id = 1950920768128811008
        request.password = '342342345'
        response = stub.UpdatePassword(request)
        print(response)
    except grpc.RpcError as e:
        print(e.code())

def test_verify_user(stub):
    request = user_pb2.VerfyUserRequest()
    request.mobile = '1882434244'
    request.password = '342342345'
    response = stub.VerifyUser(request)
    print(response)

def test_get_user_list(stub):
    request = user_pb2.PageRequest()
    request.page = 1
    request.size = 10
    response = stub.GetUserList(request)
    print(response)

def test_get_or_create_user(stub):
    try:
        request = user_pb2.MobileRequest()
        request.mobile = '188242323123124'
        response = stub.GetOrCreateUserByMobile(request)
        print(response) 
    except grpc.RpcError as e:
        print(e.code())
        print(e.details())

def main():
    with grpc.insecure_channel('localhost:5001') as channel:
        stub = user_pb2_grpc.UserStub(channel)
        test_get_or_create_user(stub)

if __name__ == '__main__':
    main()