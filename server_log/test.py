import collections
import re
from datetime import datetime


def helper(file):
    # parse time in the format of 2024-05-14 17:39:08
    def parse_time(x): return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    start_time = parse_time('2024-05-14 18:43:00')
    # duration = datetime.timedelta(hours=2)

    # open a log file and count the lines contains "get new dm cnt" and "111052"
    cnt = collections.defaultdict(int)
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # filter out the lines that are not in the time range
            time = re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
            if not time or parse_time(time.group()) < start_time:
                continue
            # DoubleDiff402: get new dm cnt: 1, _current_codeX: 101655, _current_codeY: 102539
            # regex search for _current_codeX and _current_codeY values
            result = re.search(
                r"DoubleDiff402: get new dm cnt: (\d+), _current_codeX: (\d+), _current_codeY: (\d+)", line)
            if result:
                result = result.groups()
                result = list(map(int, result))
                cnt[(result[1], result[2])] += 1

        return cnt


cnt = helper("192.168.10.203_2.log")
for k in sorted(cnt.keys()):
    if k[0] in [111052, 111891]:
        print(f"X: {k[0]}, Y: {k[1]}, count: {cnt[k]}")
