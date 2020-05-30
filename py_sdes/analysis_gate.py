from itertools import product
from collections import Counter

from func import sbox as sbox_apply
from data import S0, S1

def calcgate_sbox(sin, sbox, *, explicit=True):
	sout=sbox_apply(sin, sbox)
	return Counter({
		'X':2*(sout!=[0,0])*(4-sum(sin)),
		'CCNOT':2*(4-1)*(not explicit)+sum(sout)
	})


s0_gates=Counter()
s1_gates=Counter()
for sin in product([0,1], repeat=4):
	s0_gates+=calcgate_sbox(sin, S0)
	s1_gates+=calcgate_sbox(sin, S1)

print(s0_gates, s1_gates)