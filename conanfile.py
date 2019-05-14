from conans import ConanFile, CMake, tools
import os
import shutil

# Need to install libomp-dev in ubuntu to compile with clang or openmp in arch
# export CXXFLAGS="-std=c++14"

class MlpackConan(ConanFile):
    name = "mlpack"
    version = "3.1.0"
    license = "BSD License"
    url = "https://github.com/darcamo/conan-mlpack"
    description = "C++ machine learning library with emphasis on scalability, speed, and ease-of-use"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "link_with_mkl": [True, False],
               "use_openmp": [True, False]}
    default_options = "shared=True", "link_with_mkl=False", "use_openmp=True"
    generators = "cmake"

    def requirements(self):
        self.requires("armadillo/[>=9.200.7]@darcamo/stable")
        self.requires("boost/[>=1.68.0]@conan/stable")

        if self.options.use_openmp and tools.os_info.is_linux and self.settings.compiler == 'clang':
            # Openmp is already included in gcc, but in case of clang, a
            # separate package must be installed such that clang can compile
            # openmp programs
            installer = tools.SystemPackageTool()
            if tools.os_info.linux_distro == "ubuntu":
                installer.install("libomp-dev")
            elif tools.os_info.linux_distro == "arch":
                installer.install("openmp")

    def source(self):
        tools.get("http://www.mlpack.org/files/mlpack-{}.tar.gz".format(self.version))
        shutil.move("mlpack-{}/".format(self.version), "sources")

        tools.replace_in_file("sources/CMakeLists.txt", "project(mlpack C CXX)",
                              '''project(mlpack C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        tools.replace_in_file("sources/CMakeLists.txt", "set(MLPACK_LIBRARIES ${MLPACK_LIBRARIES} \"m\")",
                              "set(MLPACK_LIBRARIES ${MLPACK_LIBRARIES} \"m\" ${CONAN_LIBS})")

        # Remove find_package for armadillo, since we will get it from conan.
        # However, the variable 'ARMADILLO_VERSION_MAJOR' is checked and thus
        # now we need to set it.
        tools.replace_in_file("sources/CMakeLists.txt",
                              "find_package(Armadillo 6.500.0 REQUIRED)",
                              "SET(ARMADILLO_VERSION_MAJOR 9)")

    def build(self):
        os.mkdir("build")
        shutil.move("conanbuildinfo.cmake", "build/")

        cmake = CMake(self)
        # Currently if we try to build the tests we get undefined reference to
        # "boost::unit_test::unit_test_main(bool (*)(), int, char**)" when
        # building the mlpack_test target
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_CLI_EXECUTABLES"] = False
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = False

        if self.options.use_openmp:
            cmake.definitions["USE_OPENMP"] = True
        else:
            cmake.definitions["USE_OPENMP"] = False
        cmake.configure(source_folder="sources", build_folder="build")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mlpack"]
        if self.options.use_openmp:
            self.cpp_info.cppflags = ["-fopenmp"]
            self.cpp_info.sharedlinkflags = ["-fopenmp"]

        if self.options.link_with_mkl:
            # self.cpp_info.libs.extend(["mkl_rt", "hdf5"])
            self.cpp_info.libdirs.append("/opt/intel/mkl/lib/intel64")
