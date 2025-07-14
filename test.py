from data import InPgAdmin4 as inpg

if inpg.user_login('admin', '123456'):
    admin = True
print(admin)