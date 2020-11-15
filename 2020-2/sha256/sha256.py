from string import hexdigits

class SHA256:
	'''
	A SHA-256 hexdigester which takes hexadecmial string as input and outputs as hexadecimal string.
	'''
	init_hashval=('6a09e667','bb67ae85','3c6ef372','a54ff53a','510e527f','9b05688c','1f83d9ab','5be0cd19')
	round_const=('428a2f98', '71374491', 'b5c0fbcf', 'e9b5dba5', '3956c25b', '59f111f1', '923f82a4', 'ab1c5ed5',
				 'd807aa98', '12835b01', '243185be', '550c7dc3', '72be5d74', '80deb1fe', '9bdc06a7', 'c19bf174',
				 'e49b69c1', 'efbe4786', '0fc19dc6', '240ca1cc', '2de92c6f', '4a7484aa', '5cb0a9dc', '76f988da',
				 '983e5152', 'a831c66d', 'b00327c8', 'bf597fc7', 'c6e00bf3', 'd5a79147', '06ca6351', '14292967',
				 '27b70a85', '2e1b2138', '4d2c6dfc', '53380d13', '650a7354', '766a0abb', '81c2c92e', '92722c85',
				 'a2bfe8a1', 'a81a664b', 'c24b8b70', 'c76c51a3', 'd192e819', 'd6990624', 'f40e3585', '106aa070',
				 '19a4c116', '1e376c08', '2748774c', '34b0bcb5', '391c0cb3', '4ed8aa4a', '5b9cca4f', '682e6ff3',
				 '748f82ee', '78a5636f', '84c87814', '8cc70208', '90befffa', 'a4506ceb', 'bef9a3f7', 'c67178f2',)

	blocklen=512//4
	wordlen=32//4
	
	def __init__(self, data, *, debug=False):
		'''
		data
			a hexstring
		debug
			print debug strings if true; don't if false.
		'''
		if not set(data).issubset(set(hexdigits)):
			raise Exception("Input is not hexstring")
		self.data=data
		self.debug=print if debug else lambda *args, **kwargs:None
		self.chunks=None
		self.padded=None
		self.chunks=None
		self.msched=None
		self.digest=None

	def pad_data(self):
		self.debug('Data padding\n')
		l=len(self.data)*4
		length_pad=(64//4-len(hex(l)[2:]))*'0'+hex(l)[2:]
		mid_pad='8'+'0'*((SHA256.blocklen)-(l//4+len(length_pad))%(SHA256.blocklen)-1)
		self.padded=self.data+mid_pad+length_pad
		self.debug("data         : {}".format(self.data))
		self.debug("data length  : {}".format(length_pad))
		self.debug("pad length   : {}".format(len(mid_pad)))
		self.debug("total length : {}".format(len(self.padded)))
		self.debug(self.padded)

	def chunk_data(self):
		self.debug("Dividing into Chunks\n")
		self.chunks=[]
		for chunk in range(len(self.padded)//(SHA256.blocklen)):
			current=self.padded[chunk*SHA256.blocklen:(chunk+1)*SHA256.blocklen]
			self.chunks.append(current)
			self.debug("Chunk #{}\n{}".format(chunk, current))

	def schedule(self):
		self.msched=[]
		self.debug("Scheduling\n")
		for i in range(len(self.chunks)):
			sched=['0'*8 for _ in range(64)]
			chunk=self.chunks[i]

			self.debug("Chunk #{}".format(i))

			for i in range(16):
				sched[i]=chunk[i*SHA256.wordlen:(i+1)*SHA256.wordlen]

			for i in range(16,64):
				w02, w07, w15, w16 = int(sched[i-2],16), int(sched[i-7],16), int(sched[i-15],16), int(sched[i-16],16)
				s0=SHA256.rotate(w15, 7) ^ SHA256.rotate(w15,18) ^ (w15>>3)
				s1=SHA256.rotate(w02,17) ^ SHA256.rotate(w02,19) ^ (w02>>10)
				sched[i]=SHA256.int_to_word(w16+s0+w07+s1)

			for i in range(8):
				for j in range(8):
					self.debug(sched[8*i+j],end=' ')
				self.debug('')

			self.msched.append(sched)

	def hexdigest(self):
		hashval=list(map(lambda x:int(x,16),self.init_hashval))
		self.debug("Hexdigest operation in progress\n")
		self.debug("Inital hashval:",' '.join(map(SHA256.int_to_word, hashval)))
		for i in range(len(self.msched)):
			self.debug("="*SHA256.blocklen)
			self.debug("Chunk #{}".format(i))
			sched=self.msched[i]
			a,b,c,d,e,f,g,h=hashval
			self.debug("Workspace :",' '.join(map(SHA256.int_to_word,[a,b,c,d,e,f,g,h])))
			for j in range(len(sched)):
				s1 = SHA256.rotate(e,6) ^ SHA256.rotate(e,11) ^ SHA256.rotate(e,25)
				ch = (e&f)^(((2**32-1)^e)&g)
				t1 = h+s1+ch+int(SHA256.round_const[j],16)+int(sched[j],16)
				s0 = SHA256.rotate(a,2) ^ SHA256.rotate(a,13) ^ SHA256.rotate(a,22)
				maj= (a&b)^(a&c)^(b&c)
				t2 = s0+maj

				h=g
				g=f
				f=e
				e=(d+t1)%2**32
				d=c
				c=b
				b=a
				a=(t1+t2)%2**32

				self.debug("Block #{:<3}:".format(j), ' '.join(map(SHA256.int_to_word,[a,b,c,d,e,f,g,h])))
			hashval=[*map(sum, zip(hashval, [a,b,c,d,e,f,g,h]))]
		
		self.digest=''.join([*map(SHA256.int_to_word, hashval)])


	@classmethod
	def rotate(cls, num, idx):
		idx%=32
		return (num>>idx)+((num%2**idx)*2**(32-idx))%2**32

	@classmethod
	def int_to_word(cls, num):
		tmp=hex(num%2**32)[2:]
		return (SHA256.wordlen-len(tmp))*'0'+tmp

	@classmethod
	def digest(cls, data, debug=False):
		s=SHA256(data, debug=debug)
		s.pad_data()
		s.debug("="*SHA256.blocklen)
		s.chunk_data()
		s.debug("="*SHA256.blocklen)
		s.schedule()
		s.debug("="*SHA256.blocklen)
		s.hexdigest()
		return s.digest

	@classmethod
	def digest_without_pad(cls, data, debug=False):
		if len(data)%SHA256.blocklen:
			raise Exception("Only hexstring having length of which is multiple of {} is accepted".format(blocklen))
		s=SHA256(data, debug=debug)
		s.padded=data
		s.debug("="*SHA256.blocklen)
		s.chunk_data()
		s.debug("="*SHA256.blocklen)
		s.schedule()
		s.debug("="*SHA256.blocklen)
		s.hexdigest()
		return s.digest

print(SHA256.digest("", debug=True))#actual hash calculation, with debug strings
#print(SHA256.digest_without_pad('8'+"0"*127))#no padding is done; only accepts hexstring having length of which is multiple of 128(i.e. 512 bytes)
