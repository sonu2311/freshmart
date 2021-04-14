
# print(888+2)

# # Esa code likho, jisse "data/sonu.txt" bn jaye aur usme "Sonu.Saini" likha hua ho.
# import time

# int(time.time())

# # Contract: ye function input me kuch content leta hai.. aur fir jo bhi content input
# # me aya hai use ek unique file me write kr deta hai 'data/' folder me... aur us unique
# # file ka name return kr deta hai.
# def g(x):
# 	m="data/sonu"+str(int(time.time()))+".txt"
# 	f = open(m, "w")
# 	f.write(str(x))
# 	f.close()
# 	return m

# print(g("khkhkjh"))


# def f(l):
#     l1=l[0]
#     l2=l[1:]
#     list3=[]
#     for i in l2:
#         d={}
#         for j in range(len(i)):
#             d[l1[j]]=i[j]
#         list3.append (d)            
#     return list3


def import_products(l):
    l1=l[0]
    l2=l[1:]
    list3=[]
    for i in l2:
        d={}
        for j in range(len(i)):
            d[l1[j]]=i[j]
        list3.append (d)            
    return list3
print(import_products(print(f(["name","price","quantity"],[["sonu",100,1000],["mohit",10,100],["soniya",20,402]]))))


import csv

with open('abc.csv', 'r') as file:
    content = list(csv.reader(file))

print(content)