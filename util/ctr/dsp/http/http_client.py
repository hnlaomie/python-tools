import grequests, csv
from time import time

data_list = []

def predict(row_list: []):
    click_list = []
    url_list = []
    for row in row_list:
        click_list.append(row[0])
        url = 'http://192.168.11.82:50051/predict_service?data=' + ','.join(row[1:])
        url_list.append(url)
    rs = (grequests.get(u) for u in url_list)
    result_list = grequests.map(rs)    
    
    for i in range(0, len(result_list)):
        result = '-1' if result_list[i] is None else result_list[i].text
        data_list.append([click_list[i], result])
        

def load_test_data(test_file: str) -> []:
    line_list = []
    with open(test_file, 'r') as input:
        reader = csv.reader(input, delimiter=',', lineterminator='\n')
        next(reader)
        for line in reader:
            line_list.append(line)
    return line_list

line_list = load_test_data('data/show.csv')

start_time = time()

size = len(line_list)
for i in range(1, size + 1):
    remain = i % 2000
    if remain == 0:
        temp_list = line_list[i - 2000 : i]
        predict(temp_list)
    else:
        if i == size:
            temp_list = line_list[i - remain : i]
            predict(temp_list)

end_time = time()
escaped = end_time - start_time
print("用时:" + str(escaped))

#with open('data/submission_01.csv', 'w') as submission:
#    submission.write('Line,Click,Predicted\n')
#    i = 0
#    for row in data_list:
#        i += 1
#        submission.write('%d,%s,%f\n' % (i + 10000000, row[0], float(row[1])))
