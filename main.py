#!/usr/bin/env python3
import sys
import json
import pandas

data = []
data = pandas.read_json(open('./issuu_sample.json'), lines=True)