def conarr(arr):
	return ''.join(map(str, arr))

def lshift(arr, num):
	return arr[num:]+arr[:num]

def rshift(arr, num):
	return arr[-num:]+arr[:-num]

def permute(arr, perm):
	return [*map(lambda x:arr[x], perm)]

def xor(arr1, arr2):
	return [*map(lambda x:arr1[x]^arr2[x], range(len(arr1)))]

def sbox(arr, sbox):
	return [*sbox[arr[0]*2+arr[3]][arr[1]*2+arr[2]]]