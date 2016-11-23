# -*- coding: utf-8 -*-
import hashlib
from os.path import dirname, abspath
from jinja2 import Environment, FileSystemLoader

hash_code = hashlib.md5("utf-8".encode("utf-8")).hexdigest()
print(hash_code)

class Report(object):
    pass

report = Report()
report.date = "20160613"
report.impression = "1338275"
report.click = "14375"
report.uvImpression = "557254"
report.uvClick = "13545"

current_dir = dirname(abspath(__file__))
j2_env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True)
data = {"report": report}
output = j2_env.get_template('test.tmpl').render(data)
for line in output.split("\n"):
    row = line.split(",")
    print(row)