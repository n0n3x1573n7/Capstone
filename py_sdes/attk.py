from sdes import sdes
from itertools import product

def attack(p, c):
	sol=set()
	for k in product('01',repeat=10):
		if sdes(p, k)==c:
			sol.add(''.join(k))
	return sol

from time import time
t=time()
print(','.join(attack('11000111', '00010100')))
print(time()-t)