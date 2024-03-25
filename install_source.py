import os
import glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system("pip install -r requirements.txt")
print("="*20)
os.system("poetry build")
print("="*20)

try:
    import obeyon_rfs
    os.system("pip uninstall obeyon_rfs -y")
    print("="*20)
except ImportError:
    pass

#get 
for file in sorted(glob.glob(".\\dist\\*"),key=os.path.getmtime,reverse=True):
    if file.endswith(".whl"):
        os.system(f"pip install {file}")
        #we can --no-deps --force-reinstall but dependencies get skipped and not check entirely
        break