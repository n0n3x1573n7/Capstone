from data import *
from func import *
debug=lambda *args, **kwargs: None#print(*args, **kwargs)

def sdes(p, k):
	p=[*map(int, p)]
	k=[*map(int, k)]

	debug("Keygen")
	karr = keygen(k)
	debug("\nEncrypt")
	return conarr(encrypt(p, karr))

def keygen(k):
	#p10
	p=permute(k, P10)
	debug("Permuted :", conarr(p))

	k=[]
	
	for i in range(2):
		#split and round shift
		p=lshift(p[:5], i+1)+lshift(p[5:], i+1)
		debug("Split{}   :".format(i+1), conarr(p))
		
		#k1
		key=permute(p, P8)
		debug("K{}       :".format(i+1), conarr(key))

		k.append(key)
	
	return k

def encrypt(p, k):
	#IP
	p1=permute(p, IP)
	debug("IP       :", conarr(p1),'\n')

	for i in range(2):
		#L/R separation of p1
		l, r=p1[:4], p1[4:]
		debug("L{}       :".format(i+1), conarr(l))
		debug("R{}       :".format(i+1), conarr(r))

		#EP
		e=permute(r, EP)
		debug("E{}       :".format(i+1), conarr(e))

		#XOR with key
		x=xor(e, k[i])
		debug("X{}       :".format(i+1), conarr(x))

		#L/R separation of xor-ed key
		xl, xr = x[:4], x[4:]
		debug("XL{}      :".format(i+1), conarr(xl))
		debug("XR{}      :".format(i+1), conarr(xr))

		#S-box application
		s0 = sbox(xl, S0)
		debug("s0-{}     :".format(i+1), conarr(s0))
		s1 = sbox(xr, S1)
		debug("s1-{}     :".format(i+1), conarr(s1))
		s = s0+s1
		debug("S{}       :".format(i+1), conarr(s))

		#P4
		ps = permute(s, P4)
		debug("PS{}      :".format(i+1), conarr(ps))

		#ps XOR L
		xpl = xor(ps, l)
		debug("XPL{}     :".format(i+1), conarr(xpl))

		#swap concat
		p1=r+xpl
		debug("Rd{} Res  :".format(i+1), conarr(p1),'\n')

	#undo swap
	p_unswap=p1[4:]+p1[:4]
	debug("Unswap   :", conarr(p_unswap))

	#IP_inv
	ipinv=permute(p_unswap, IP_inv)
	debug("Result   :", conarr(ipinv))

	return ipinv