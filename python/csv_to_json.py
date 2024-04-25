#!/usr/bin/env python
import csv
import json

csv_file_path = 'cross_border.csv'


# csv 파일 읽어오기
with open(csv_file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # 첫 줄 skip

    # 각 라인마다 딕셔너리 생성 후 리스트에 추가
    data = []
    for line in reader:
        # if len(data) == 0:
        #     data.
        d = {
            '상품군별(1)': str(line[0].strip()),
            '2019': int(line[1]),
            '20191': int(line[2]),
            '20192': float(line[3]),
            '2020': int(line[4]),
            '20201': int(line[5]),
            '20202': float(line[6]),
            '2021': int(line[7]),
            '20211': int(line[8]),
            '20212': float(line[9]),
            '2022': int(line[10]),
            '20221' : int(line[11]),
            '20222' : float(line[12]),
            '2023' : int(line[13]),
            '20231' : int(line[14]),
            '20232' : float(line[15])
        }
        data.append(d)

# json string으로 변환
data = {'cross_border': data}
json_string = json.dumps(data, ensure_ascii=False, indent=2)

print(json_string)

# txt 파일로 저장할 경로
txt_file_path = 'cross_border_data.json'

# txt 파일 쓰기
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(json_string)