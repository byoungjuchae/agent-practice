list = ["one", "two", "three"]
for index in list :
  print(index)

number = 0
while number < 10:
  number = number + 1
  print(f"지금 숫자는{number}")
  if number == 10:
    print("숫자 끝")

def test(a, b):
  print(f"a 더하기 b는 {a + b}")

test(1, 3)