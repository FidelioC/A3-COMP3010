import random

my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

random_choices = random.sample(my_list, 3)
print(random_choices[1])
print("Three different random choices:", random_choices)