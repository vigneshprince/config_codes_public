# %%
import pikepdf
import os
while True:
    try:
        file=input("Enter the file name: ")
        password=input("Enter the password: ")
        new_path=os.path.join(os.path.dirname(file),'unlocked_'+os.path.basename(file))
        with pikepdf.open(file,password=password) as p:
            p.save(new_path)
        print("File saved : ",new_path)
    except Exception as e:
        print(e)

