#!/usr/bin/env python3

import yaml
from pathlib import Path

# Vygeneruje niekoľko súborov v podadresári data

elephant={'name':'Elephant','family':'Elephantidae','legs':4,'eats':['grass','leaves']}
cat={'name':'Cat','family':'Felis','legs':4,'eats':['rodents','birds']}
python={'name':'Python','family':'Felis','legs':0,'eats':['small mammals','birds','reptiles']}

for key,animal in (('elephant',elephant),('cat',cat),('python',python)):
    with open(Path('data',f'{key}.yaml'),mode='w') as f:
        f.write(yaml.dump(animal,sort_keys=False)) # netriediť

# Prečíta ich a spracuje
for fnm in Path('data').glob('*.yaml'):
    with open(fnm) as f:
        d=yaml.safe_load(f)
        print(d['name'],d['eats'])
