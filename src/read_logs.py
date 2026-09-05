def read_logs(filename):
    with open(filename,'r') as file:
        logs = file.readlines()
        return logs

logs = read_logs("data/sample.log")
for log in logs:
    print(log.strip())