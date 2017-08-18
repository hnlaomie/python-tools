import socket, csv
from time import time

def load_test_data(test_file: str) -> []:
    line_list = []
    with open(test_file, 'r') as input:
        reader = csv.reader(input, delimiter=',', lineterminator='\n')
        next(reader)
        for line in reader:
            line_list.append(line)
    return line_list

if __name__ == "__main__":
    line_list = load_test_data('/home/laomie/projects/python/data/show.csv')
    data_list = []
    start_time = time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 50051))
    i = 0
    for line in line_list:
        click = line[0]
        data = ','.join(line[1:])
        sock.sendall(data.encode())
        result = sock.recv(128)
        data_list.append([click, result.decode()])
        i += 1
        if i % 20000 == 0:
            print('finish ' + str(i))
        #print(result)
    sock.close()
    end_time = time()
    escaped = end_time - start_time
    print("用时:" + str(escaped))

    with open('/home/laomie/projects/python/data/submission_01.csv', 'w') as submission:
        submission.write('Line,Click,Predicted\n')
        i = 0
        for row in data_list:
            i += 1
            submission.write('%d,%s,%f\n' % (i + 10000000, row[0], float(row[1])))
