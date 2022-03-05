import listen_eth_event as lee
import time
import threading


# 运行前请修改下面的东西
rpcAddr = 'HTTP://127.0.0.1:7545'
contractAddr = '0xcc11Ba9e7bbD137c1535F7115Eb34755d636eAea'
acc1 = '0x65968c459F61a5A332d3fb5C4c0Ae5aD18babbdE'  # 执行初始化 第一次上传的账户
acc2 = '0x0C35a782c71ff9f927eaA1A16662107441f6Fa46'  # 执行加入任务 第二次上传的账户
max_req_times = 60  # thread等待时间 超时自动退出
interval = 2
taskID = 1

ll = lee.Listener(rpcAddr, contractAddr, max_req_times, interval)


def th_1(account_address, ret):
    if ll.init_task_event(taskID, account_address):
        print("init_task_event succ")
        ret.append(True)
    else:
        print("Related init_task_event not find in ", max_req_times, " times")
        ret.append(False)
    return


def th_2(account_address, ret):
    if ll.update_task_event(taskID, account_address):
        print("update_task_event succ")
        ret.append(True)
    else:
        print("Related update_task_event not find in ", max_req_times, " times")
        ret.append(False)
    return


def th_3(account_address, ret):
    if ll.record_event(taskID, account_address, 1, 1, 1):
        print("record_event succ", account_address)
        ret.append(True)
    else:
        print("Related record_event not find in ", max_req_times, " times")
        ret.append(False)
    return "custom_ret_value", 3


def th_4(layer, w_or_b, offset, ret):
    if ll.gift_prepare_event(taskID, layer, w_or_b, offset):
        print("gift_prepare_event succ")
        ret.append(True)
    else:
        print("Related gift_prepare_event not find in ", max_req_times, " times")
        ret.append(False)
    return "custom_ret_value", 4


global thread_ret
thread_ret = []

start_time = time.time()
threads = []  # 创建线程数组
thread1 = threading.Thread(target=th_1, args=(acc1, thread_ret))
# Init task 与 update task的人/账户不能是同一个
thread2 = threading.Thread(target=th_2, args=(acc2, thread_ret))
thread3_1 = threading.Thread(target=th_3, args=(acc1, thread_ret))
# 下面这一行不会返回成功 因为测试case所需要的节点数是2 当节点数满足的时候会改为触发gift_prepare_event事件
thread3_2 = threading.Thread(target=th_3, args=(acc2, thread_ret))
thread4 = threading.Thread(target=th_4, args=(1, 1, 1, thread_ret))

threads.append(thread1)  # 将线程1添加到线程数组
threads.append(thread2)
threads.append(thread3_1)
threads.append(thread3_2)
threads.append(thread4)

for i in threads:
    i.start()  # 启动线程

for i in threads:
    i.join()  #

run_times = (time.time()-start_time)
print('主线程和子线程运行时间共：%s' % run_times)
print(thread_ret)

