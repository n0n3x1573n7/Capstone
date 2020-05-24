from sdes import sdes
from func import conarr
from itertools import product
from collections import Counter
from pickle import dumps, loads

try:
	keycount=loads(open('analysis.pkl','rb').read())
except:
	keycount=Counter()
	for p, k in product(product('01',repeat=8), product('01',repeat=10)):
		print(conarr(p), conarr(k), conarr(c:=sdes(p,k)))
		keycount[conarr(p)+'->'+conarr(c)]+=1
	with open('analysis.pkl','wb') as f:
		f.write(dumps(keycount))

cnt=Counter()
for i in keycount.values():
	cnt[i]+=1