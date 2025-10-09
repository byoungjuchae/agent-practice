var1 = 1
var2 = "2"
var3 = [1,2,"3"]
var4 = {"key" : 1}

print(var1)
print(var2)
print(var3)
print(var4.get("key"))

for index, value in enumerate(var3):
    print(f"index {index} value {value}")


