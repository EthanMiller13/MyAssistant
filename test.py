the_code = '''
a = 1
b = 2
return_me = a + b
'''

loc = {}
exec(the_code, globals(), loc)
return_workaround = loc['return_me']
print(return_workaround)  # 3