import string
# help

'''
+ All variables are 32-bit words.
+ w00, w01, ..., w15    : input value
+ w16, w17, ..., w63    : additional stretched words from input, possibly not necessary?
+ a, b, ..., h          : output hash
+ k00, k01, ..., k63    : predetermined constant (by cubic root derp, not necessary)
+ s0                    : (a >> 2) ^ (a >> 13) ^ (a >> 22)
+ s1                    : (e >> 6) ^ (e >> 11) ^ (e >> 25)
+ ch                    : (e & f) ^ (~e & g)
+ t1                    : h + s1 + ch + k[i] + w[i]
+ maj                   : (a & b) ^ (a & c) ^ (b & c)
+ t2                    : s0 + maj
(then d <- d + t1, a <- t1 + t2, permute)
'''
round_const=('428a2f98', '71374491', 'b5c0fbcf', 'e9b5dba5', '3956c25b', '59f111f1', '923f82a4', 'ab1c5ed5',
             'd807aa98', '12835b01', '243185be', '550c7dc3', '72be5d74', '80deb1fe', '9bdc06a7', 'c19bf174',
             'e49b69c1', 'efbe4786', '0fc19dc6', '240ca1cc', '2de92c6f', '4a7484aa', '5cb0a9dc', '76f988da',
             '983e5152', 'a831c66d', 'b00327c8', 'bf597fc7', 'c6e00bf3', 'd5a79147', '06ca6351', '14292967',
             '27b70a85', '2e1b2138', '4d2c6dfc', '53380d13', '650a7354', '766a0abb', '81c2c92e', '92722c85',
             'a2bfe8a1', 'a81a664b', 'c24b8b70', 'c76c51a3', 'd192e819', 'd6990624', 'f40e3585', '106aa070',
             '19a4c116', '1e376c08', '2748774c', '34b0bcb5', '391c0cb3', '4ed8aa4a', '5b9cca4f', '682e6ff3',
             '748f82ee', '78a5636f', '84c87814', '8cc70208', '90befffa', 'a4506ceb', 'bef9a3f7', 'c67178f2',)

def var(pre, num=None):
    if num == None:
        return pre
    return pre + str(num).rjust(2, '0')

g_ch = '''
gate ch a,b,c,r
{
    cx c,res;
    cx b,c;
    ccx a,c,r;
}
gate ch_a a,b,c,r
{
    ccx a,c,r;
    cx b,c;
    cx c,r;
}
'''
g_majr = '''
gate majr a,b,c,r
{
    ccx a,b,r;
    cx a,b;
    ccx b,c,r;
}
gate majr_a a,b,c,r
{
    ccx b,c,r;
    cx a,b;
    ccx a,b,r;
}
'''
g_adder_32 = '''
gate maj a,b,c
{
  cx c,b;
  cx c,a;
  ccx a,b,c;
}
gate uma a,b,c
{
  ccx a,b,c;
  cx c,a;
  cx a,b;
}

gate add32 a00,a01,a02,a03,a04,a05,a06,a07,a08,a09,a10,a11,a12,a13,a14,a15,a16,a17,a18,a19,a20,a21,a22,a23,a24,a25,a26,a27,a28,a29,a30,a31,b00,b01,b02,b03,b04,b05,b06,b07,b08,b09,b10,b11,b12,b13,b14,b15,b16,b17,b18,b19,b20,b21,b22,b23,b24,b25,b26,b27,b28,b29,b30,b31,cin
{
  maj cin,b00,a00;
  maj a00,b01,a01;
  maj a01,b02,a02;
  maj a02,b03,a03;
  maj a03,b04,a04;
  maj a04,b05,a05;
  maj a05,b06,a06;
  maj a06,b07,a07;
  maj a07,b08,a08;
  maj a08,b09,a09;
  maj a09,b10,a10;
  maj a10,b11,a11;
  maj a11,b12,a12;
  maj a12,b13,a13;
  maj a13,b14,a14;
  maj a14,b15,a15;
  maj a15,b16,a16;
  maj a16,b17,a17;
  maj a17,b18,a18;
  maj a18,b19,a19;
  maj a19,b20,a20;
  maj a20,b21,a21;
  maj a21,b22,a22;
  maj a22,b23,a23;
  maj a23,b24,a24;
  maj a24,b25,a25;
  maj a25,b26,a26;
  maj a26,b27,a27;
  maj a27,b28,a28;
  maj a28,b29,a29;
  maj a29,b30,a30;
  maj a30,b31,a31;
  uma a30,b31,a31;
  uma a29,b30,a30;
  uma a28,b29,a29;
  uma a27,b28,a28;
  uma a26,b27,a27;
  uma a25,b26,a26;
  uma a24,b25,a25;
  uma a23,b24,a24;
  uma a22,b23,a23;
  uma a21,b22,a22;
  uma a20,b21,a21;
  uma a19,b20,a20;
  uma a18,b19,a19;
  uma a17,b18,a18;
  uma a16,b17,a17;
  uma a15,b16,a16;
  uma a14,b15,a15;
  uma a13,b14,a14;
  uma a12,b13,a13;
  uma a11,b12,a12;
  uma a10,b11,a11;
  uma a09,b10,a10;
  uma a08,b09,a09;
  uma a07,b08,a08;
  uma a06,b07,a07;
  uma a05,b06,a06;
  uma a04,b05,a05;
  uma a03,b04,a04;
  uma a02,b03,a03;
  uma a01,b02,a02;
  uma a00,b01,a01;
  uma cin,b00,a00;
}'''

qregs = "abcdefght"
def q_xor_qubit(src, dst):
    print(f'cx {src},{dst};')

def q_xor(src, dst, rsh):
    assert 0 <= rsh < 32
    for i in range(rsh, 32):
        q_xor_qubit(src + f"[{i}]", dst + f"[{i-rsh}]")

def q_add(src, dst):
    print('add32 ', ','.join(
        [src + f'[{i}]' for i in range(32)] +
        [dst + f'[{i}]' for i in range(32)] +
        ['cin[0]']), ';', sep='')

def q_x(a):
    print(f'x {a};')

def q_ch(a, b, c, d):
    print(f'ch {a},{b},{c},{d};')

def q_ch_a(a, b, c, d):
    print(f'ch_a {a},{b},{c},{d};')

def q_majr(a, b, c, r):
    print(f'majr {a},{b},{c},{r};')

def q_majr_a(a, b, c, r):
    print(f'majr_a {a},{b},{c},{r};')

def prepare():
    print('''OPENQASM 2.0;
include "qelib1.inc";''')

    print('// Functions ')
    print(g_adder_32)
    print(g_ch)
    print(g_majr)
    print()
    print('// Registries')
    for ch in qregs:
        print('qreg {}[32];'.format(ch))
    for i in range(16):
        print('qreg w{:02d}[32];'.format(i))
    print('creg res[32];')
    print('qreg cin[1];')
    print()

    print('// set input')
    print()

ind = lambda i, r : (i + 8 - (r & 7)) & 7
wind = lambda x : '{:02d}'.format(x & 15) # x >= 0
prepare()
for round_num in range(64):
    print(f'// Round {round_num+1}')
    print('// [+] Calculating s1')
    for rsh in [6, 11, 25]:
        q_xor(qregs[ind(4, round_num)], qregs[-1], rsh)
    q_add(qregs[-1], qregs[ind(7, round_num)])
    for rsh in [6, 11, 25]:
        q_xor(qregs[ind(4, round_num)], qregs[-1], rsh)

    print('// [+] Calculating Ch')
    q_ch(qregs[ind(4, round_num)], qregs[ind(5, round_num)],
         qregs[ind(6, round_num)], qregs[-1])

    q_add(qregs[-1], qregs[ind(7, round_num)])

    q_ch_a(qregs[ind(4, round_num)], qregs[ind(5, round_num)],
         qregs[ind(6, round_num)], qregs[-1])

    print('// [+] Calculating k[i]')
    for i in range(32):
        if int(round_const[round_num], 16) & (1 << i):
            q_x(qregs[-1] + f'[{i}]')
    q_add(qregs[-1], qregs[ind(7, round_num)])
    for i in range(32):
        if int(round_const[round_num], 16) & (1 << i):
            q_x(qregs[-1] + f'[{i}]')

    print('// [+] Calculating w[i]')
    if round_num >= 16:
        for rsh in [7, 18, 3]:
            q_xor('w'+wind(round_num - 15), qregs[-1], rsh)
        q_add(qregs[-1], 'w'+wind(round_num))
        for rsh in [7, 18, 3]:
            q_xor('w'+wind(round_num - 15), qregs[-1], rsh)

        for rsh in [17, 19, 10]:
            q_xor('w'+wind(round_num - 2), qregs[-1], rsh)
        q_add(qregs[-1], 'w'+wind(round_num))
        for rsh in [17, 19, 10]:
            q_xor('w'+wind(round_num - 2), qregs[-1], rsh)

        q_add('w'+wind(round_num - 7), 'w'+wind(round_num))

    print('// [+] Add w[i]')
    q_add('w'+wind(round_num), qregs[ind(7, round_num)])

    print('// [+] Add h to d')
    q_add(qregs[ind(7, round_num)], qregs[ind(3, round_num)])

    print('// [+] Calculate Maj')
    q_majr(qregs[ind(0, round_num)], qregs[ind(1, round_num)], qregs[ind(2, round_num)], qregs[-1])

    q_add(qregs[-1], qregs[ind(7, round_num)])

    q_majr_a(qregs[ind(0, round_num)], qregs[ind(1, round_num)], qregs[ind(2, round_num)], qregs[-1])

    print('// [+] Calculate s0')
    for rsh in [2, 13, 22]:
        q_xor(qregs[ind(0, round_num)], qregs[-1], rsh)
    q_add(qregs[-1], qregs[ind(7, round_num)])
    for rsh in [2, 13, 22]:
        q_xor(qregs[ind(0, round_num)], qregs[-1], rsh)






