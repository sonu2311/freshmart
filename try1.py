print(2+4)

import time


# Contract: ye function input me kuch content leta hai.. aur fir jo bhi content input
# me aya hai use ek unique file me write kr deta hai 'data/' folder me... aur us unique
# file ka name return kr deta hai.

def new_function(x):
	v="data/pooja"+str(int(time.time()))+".txt"
	f = open(v , "w")
	f.write(str(x))
	f.close()
	return v
print(new_function("xjkhkhk"))