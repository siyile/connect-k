import sys
sys.path.append("../../connect-k-python")
sys.path.append("../../connect-k-python/AI_Extensions")
sys.path.append("../connect-k-python")
sys.path.append("../connect-k-python/AI_Extensions")

from GameLogic import GameLogic



from socket import *
def network_init():
    serverPort = 12002
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('syn2-1.ics.uci.edu', serverPort))

    sentence = "REQUEST_NUM"
    clientSocket.send(sentence.encode())
    result = int(clientSocket.recv(1024).decode())
    clientSocket.close()

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.connect(('syn2-1.ics.uci.edu', serverPort))

    print("There are currently",result,"rooms.")
    print("Enter which room you want to join, or create a new room.")
    while True:
        command = input('{# of room/create}')
        try:
            int(command)
            sentence = "REQUEST_JOIN|"+command
            mode = 'client'
        except:
            if command != "create":
                print("Unknown Command")
                continue
            else:
                sentence = "REQUEST_OPEN"
                mode = 'host'

        clientSocket.send(sentence.encode())

        response = eval(clientSocket.recv(1024).decode())
        clientSocket.close()
        return response,mode

def run(col,row,k,ai_path_1,ai_path_2,fh,mode='t',full_path = None):
    if full_path is not None:
        ai_path_1 = full_path + ai_path_1
        ai_path_2 = full_path + ai_path_2
    main = GameLogic(col,row,k,'l',debug=True)
    return main.Run(fh=fh,mode=mode,ai_path_1=ai_path_1,ai_path_2=ai_path_2,time=1200)


if __name__ == "__main__":
    # To run under manual mode, please use this command "python3 main.py {row} {col} {k} m {order}"
    # e.g. "python3 main.py 7 7 2 m 0"
    # e.g. "python3 main.py 7 7 2 l {AI_path 1} {AI_path 2}"
    # e.g. "python3 main.py 7 7 2 n {AI_path}"

    # Because the initialization of network mode is different from the normal modes,
    # the initialization of network mode is separated from other modes.
    if len(sys.argv) == 3:
        mode = sys.argv[1]
        if mode == 'n' or mode == 'network':
            ai_path = sys.argv[2]
            response,host_flag, rule = network_init()

            rule = list(map(lambda x:int(x),rule))

            col, row, k,g, order = rule

            main = GameLogic(col, row, k,g, 'n', debug=True)
            try:
                main.Run(mode=host_flag, ai_path=ai_path, info=response, time=1200)
            except:
                import traceback
                traceback.print_exc()
                import threading
                for timer in threading.enumerate():
                    if type(timer) == threading.Timer:
                        timer.cancel()
            exit(0)
        else:
            print("Invalid Parameters")
            sys.exit(-1)

    if len(sys.argv) < 5:
        print("Invalid Parameters")
        sys.exit(-1)

    col = int(sys.argv[1])
    row = int(sys.argv[2])
    k = int(sys.argv[3])
    g = int(sys.argv[4])
    mode = sys.argv[5]

    main = GameLogic(col,row,k,g,mode,debug=True)

    if mode == 'm' or mode == 'manual':
        order = sys.argv[6]
        order =main.Run(mode=mode,order=order)

    elif mode == 't':
        main.Run(mode=mode)

    elif mode == 's' or mode == 'self':
        order = sys.argv[6]
        main.Run(mode=mode,order=order)

    elif mode == 'l':
        ai_path_1,ai_path_2 =  sys.argv[6],sys.argv[7]
        main.Run(mode=mode,ai_path_1=ai_path_1,ai_path_2=ai_path_2,time=1200)
