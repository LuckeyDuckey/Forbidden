import os, shutil, pybind11
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# Build Instructions:
#   - Run this from inside the CppSource directory:
#       python setup.py build_ext --inplace
#   - If you have multiple Python versions, you can run:
#       py -3.8 setup.py build_ext --inplace
#   - Make sure to replace 3.8 with your python version

SourceDirectory = os.path.abspath(os.path.dirname(__file__))
BuildDirectory = os.path.abspath(os.path.join(SourceDirectory, "..", "CppBuild"))

class CustomBuildExtension(build_ext):
    def run(self):
        super().run()

        # Remove temp files made during build process
        TempBuildFolder = os.path.join(SourceDirectory, "build")
        if os.path.exists(TempBuildFolder):
            shutil.rmtree(TempBuildFolder)

        # Move compiled files to CppBuild
        for Extension in self.extensions:
            CurrentBuildFilePath = self.get_ext_fullpath(Extension.name)
            TargetBuildFilePath = os.path.join(BuildDirectory, os.path.basename(CurrentBuildFilePath))
            shutil.move(CurrentBuildFilePath, TargetBuildFilePath)

setup(
    name="Simulations",
    ext_modules=[
        Pybind11Extension(
            name = "Simulations",
            sources = [
                "Bindings.cpp",
                "VectorMath.cpp",
                "VerletChain.cpp",
                "Boid.cpp",
            ],
        )
    ],
    cmdclass = {"build_ext": CustomBuildExtension},
)
