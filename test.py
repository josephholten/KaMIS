response = input("please respond: Y/n")
if response == "" or response.lower() == "y":
    print("you responded with: y")
elif response.lower() == "n":
    print("you responded with: n")
else:
    print("invalid response")

