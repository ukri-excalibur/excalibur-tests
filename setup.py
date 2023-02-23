import shutil

print("Installation or excalibur-tests is done!")
if not shutil.which("spack"):
    print("To run the apps in reframe, you have to provide an installation of spack in PATH")
    print("We cannot yet install spack automatically, please follow instructions in")
    print("README.md to install spack.")

else:
    print("Spack was found in PATH. You are good to go!")
