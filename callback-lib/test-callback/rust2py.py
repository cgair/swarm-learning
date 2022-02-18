from callback_api import run_grpc_server
import os



if __name__ == '__main__':
    # 设置环境变量
    os.environ['GRPC_LOG']="info"
    
    print(run_grpc_server())
