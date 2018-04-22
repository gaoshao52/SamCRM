from django.test import TestCase

# Create your tests here.

from django.core.paginator import Paginator

objs = []
for i in range(10, 1000):
    objs.append(i)


p = Paginator(objs, 20)
print(p.count)
print(p.num_pages)

print(p.page_range)

page1 = p.page(1)
print(page1)


page2 = p.page(2)
print(page2.number)

print(page2)
print(page2.object_list)
print(page2.next_page_number())

print(page2.paginator.page_range)


