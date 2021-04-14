import csv

with open('abcd.csv', 'r') as file:
    content = list(csv.reader(file))

print(content)