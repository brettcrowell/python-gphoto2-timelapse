import json
from sequence import Sequence
from pprint import pprint

seq = Sequence("data_file")

print(seq.get_next_image())

#with open('data.json') as data_file:
#    data = json.load(data_file)

#pprint(data)