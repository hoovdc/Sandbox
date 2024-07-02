#list test

#create a sample list of lists to demonstrate sequence of how dimensions are referenced
my_list = [["inner list 0 item 0" , "inner list 0 item 1" ,"inner list 0 item 2"],
           ["inner list 1 item 0" , "inner list 1 item 1" ,"inner list 1 item 2"],
           ["inner list 2 item 0" , "inner list 2 item 1" ,"inner list 2 item 2"]]

#print the position and contents of each item in the list
for i in range(len(my_list)):
    for j in range(len(my_list[i])):
        print(f"[{i}][{j}]      Row {i} Column {j}     {my_list[i][j]}")

#print the combined contents of each row in the list
for i in range(len(my_list)):
    print(f"Row {i} : {my_list[i]}")

#print the combined contents of each column in the list
for i in range(len(my_list[0])):
    print(f"Column {i} : {[my_list[j][i] for j in range(len(my_list))]}")

