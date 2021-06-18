import math
import sys
def block(user_input):
    msg = ""
    for i in range(len(user_input)):
        if user_input[i] != " ":
            msg += user_input[i]
    for i in range(len(msg)):
        if msg[i] not in ["0", "1", "2", "3"]:
            msg = "Error"
    return msg

def md2(msg):
    msg = [int(c) for c in msg]
    BLOCK_SIZE = 16
    padding_pat = BLOCK_SIZE - (len(msg) % BLOCK_SIZE)
    padding = padding_pat * [padding_pat % 4]
    msg = msg + padding
    N = len(msg)
    s_box = [1, 3, 0, 2]
    checksum = 16 * [0]
    l = 0
    blocks = math.ceil(N / BLOCK_SIZE)
    for i in range(blocks):
        for j in range(BLOCK_SIZE):
            l = s_box[(msg[i*BLOCK_SIZE+j] ^ l)] ^ checksum[j]
            checksum[j] = l
    msg = msg + checksum
    blocks += 1
    md_digest = 48 * [0]
    for i in range(blocks):
        for j in range(BLOCK_SIZE):
            md_digest[BLOCK_SIZE+j] = msg[i*BLOCK_SIZE+j]
            md_digest[2*BLOCK_SIZE+j] = (md_digest[BLOCK_SIZE+j] ^ md_digest[j])
            checktmp = 0
        for j in range(18):
            for k in range(48):
                checktmp = md_digest[k] ^ s_box[checktmp]
                md_digest[k] = checktmp
            checktmp = (checktmp+j) % 4
    return(" ".join(map(str, md_digest[0:16])))

def compress(h_i, m_block):
    md_digest = 48 * [0]
    for i in range(len(h_i)):
        md_digest[i] = int(h_i[i])
        md_digest[i+16] = int(m_block[i])
        md_digest[i+32] = int(h_i[i]) ^ int(m_block[i])
    s_box = [1, 3, 0, 2]
    checktmp = 0
    for j in range(18):
        for k in range(48):
            checktmp = md_digest[k] ^ s_box[checktmp]
            md_digest[k] = checktmp
        checktmp = (checktmp+j) % 4
    return(" ".join(map(str, md_digest[0:16])))

def string_sbox(Matrix, num):
    s = [1, 3, 0, 2]
    for i in range(1, 16):
        Matrix[num][i] = Matrix[num-1][i] ^ s[Matrix[num][i-1]]
    return Matrix

def Matrix_init(Matrix):
    s = [1, 3, 0, 2]
    r_s = [2, 0, 3, 1]
    Matrix[1][0] = Matrix[0][0] ^ s[0]
    Matrix = string_sbox(Matrix, 1)
    Matrix = string_sbox(Matrix, 2)
    for i in range(17,2,-1):
        for j in range(19-1-i, 16):
            Matrix[i][j] = Matrix[i+1][j] ^ s[Matrix[i+1][j-1]]
    for i in range(3, 17):
        for j in range(16-(i-1), -1, -1):
            Matrix[i][j] = r_s[Matrix[i][j+1] ^ Matrix[i-1][j+1]]
    if Matrix[19][0] != 0:
        Matrix[19][0][1][15] = r_s[Matrix[2][0] ^ Matrix[1][0]]
        Matrix[19][0][2][15] = (r_s[Matrix[3][0] ^ Matrix[2][0]] + 3) % 4
        Matrix[19][0][3][15] = (r_s[Matrix[4][0] ^ Matrix[3][0]] + 2) % 4
        Matrix[19][0][4][15] = (r_s[Matrix[5][0] ^ Matrix[4][0]] + 1) % 4

def to_4(Matrix, num):
    for i in range(1, 5):
        Matrix[i][15] = num & 0b11
        num >>= 2
        return Matrix
def to_4_1(num):
    return([num//(4**15), (num%4**15)//(4**14), (num%4**14)//(4**13), (num%4**13)//(4**12), (num%4**12)//(4**11), (num%4**11)//(4**10), (num%4**10)//(4**9), (num%4**9)//(4**8), 0, 0, 0, 0, 0, 0, 0, 0])

def to_4_2(num):
    return([0, 0, 0, 0, 0, 0, 0, 0, num // (4**7), (num % 4**7)//(4**6), (num % 4**6)//(4**5), (num % 4**5)//(4**4), (num % 4**4)//(4**3), (num % 4**3)//(4**2), (num % 4**2)//(4**1), (num % 4)])

def matrix_sbox(Matrix):
    s = [1, 3, 0, 2]
    for i in range(1,5):
        Matrix[i][0] = Matrix[i-1][0] ^ s[Matrix[19][0][i][15]]
    for i in range(1,5):
        for j in range(1,8):
            Matrix[i][j] = Matrix[i-1][j] ^ s[Matrix[i][j-1]]

def values(B, C):
    res = 0
    for i in range(1,5):
        tmp_b = 0
        tmp_c = 0
        tmp_b = B[i][7]
        tmp_b <<= 2 * (i-1)
        res ^= tmp_b
        tmp_c = C[i][7]
        tmp_c <<= (8 + 2 * (i-1))
        res ^= tmp_c
    return res

def dictionary_init(dictionary, A, B, C):
    m = 0
    B[19][0] = A
    C[19][0] = B
    for m in range(0 , 4294901761, 65536):
        B[0] = to_4_1(m)
        for i in range(16):
            C[0][i] = A[0][i] ^ B[0][i]
        matrix_sbox(B)
        matrix_sbox(C)
        dictionary[values(B, C)] = 4294901761 - m

def matrix_r_sbox(Matrix):
    r_s = [2, 0, 3, 1,]
    for i in range(1, 5):
        for j in range(14, 6, -1):
            Matrix[i][j] = r_s[Matrix[i][j+1] ^ Matrix[i-1][j+1]]

def find_collisions(dictionary, h0, h1, msg, A, B, C):
    for m in range(65536):
        B[0] = to_4_2(m)
        for i in range(16):
            C[0][i] = A[0][i] ^ B[0][i]
        matrix_r_sbox(B)
        matrix_r_sbox(C)
        if values(B, C) in dictionary:
            tmp =""
            for i in range(16):
                tmp += str(to_4_2(m)[i] ^ to_4_1(dictionary[values(B,C)])[i])
            if " ".join(map(str, h1)) == compress(h0, tmp):
                for i in range(16):
                    msg.append((to_4_1(dictionary[values(B,C)])[i] ^ to_4_2(m)[i]))
                return True
    return False        



def preimage(h_0, h_1):
    A = [[[0 for i in range(16)] for j in range(20)] for k in range(4)]
    C = [[[0 for i in range(16)] for j in range(20)] for k in range(4)]
    for i in range(4):
        for j in range(len(h_0)):
            A[i][0][j] = int(h_0[j])
        for j in range(len(h_1)):
            A[i][18][j] = int(h_1[j])
        A[i][19][0] = C[i]
        A[i][2][0] = i
        Matrix_init(A[i])
    B = [[[0 for i in range(16)] for j in range(20)] for k in range(256)]
    msg = []
    for i in range(256):
        B[i] = to_4(B[i], i)
    for i in range(4):
        for j in range(256):
            dictionary = {}
            dictionary_init(dictionary, A[i], B[j], C[i])
            if find_collisions(dictionary, h_0, h_1, msg, A[i], B[j], C[i]):
                return msg
    return msg


if sys.argv[1] == "md2":
    msg = ""
    for i in range(2, len(sys.argv)):
        msg += block(sys.argv[i])
    if "Error" in msg:
        print("Некорректный ввод!")
    else:
        print(md2(msg))
elif sys.argv[1] == "compress":
    if len(sys.argv) < 4 :
        print("Некорректный ввод!")
    elif block(sys.argv[2]) == "Error" or block(sys.argv[3]) == "Error":
        print("Некорректный ввод!")
    else:
        print(compress(block(sys.argv[2]), block(sys.argv[3])))
elif sys.argv[1] == "preimage":
    if len(sys.argv) < 4 :
        print("Некорректный ввод!")
    elif block(sys.argv[2]) == "Error" or block(sys.argv[3]) == "Error":
        print("Некорректный ввод!")
    else:
        print(" ".join(map(str, preimage(block(sys.argv[2]), block(sys.argv[3])))))

else:
    print("Некорректный ввод!")
#python3 md2.py md2 "0 3 1 2 1 1 0 2 0 3 3 0 1 1 2 0" "3 2 2 2 2 2 1 0 0 3 3 0 1 2 3 0"
#python3 md2.py compress "1 3 2 2 0 2 1 0 0 3 3 0 1 2 3 0" "1 2 0 2 3 1 0 2 0 3 3 0 1 1 2 0"
#python3 md2.py preimage "0 1 2 3 0 1 2 3 0 1 2 3 0 1 2 3" " 0 0 3 2 2 2 1 0 0 0 3 0 3 3 1 2"
#python3 md2.py compress "0 1 2 3 0 1 2 3 0 1 2 3 0 1 2 3" "0 0 0 0 3 3 1 3 0 0 0 0 0 0 0 0"
#python3 md2.py preimage "3 2 2 2 2 0 0 2 0 3 2 0 1 0 3 1" "0 0 3 3 0 2 1 1 0 3 3 0 2 2 1 1"
#python3 md2.py compress "3 2 2 2 2 0 0 2 0 3 2 0 1 0 3 1" "0 0 0 0 3 2 2 2 0 0 0 0 0 0 0 0"
