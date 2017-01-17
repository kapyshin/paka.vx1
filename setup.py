import sys
import setuptools


PY2 = sys.version_info.major == 2


def _get_install_requirements():
    requirements = [
        "six", "mako", "markupsafe", "paka.cmark",
        "paka.feedgenerator", "paka.webstatic"]
    if PY2:
        requirements.append("enum34")
    return requirements

def _get_testing_requirements():
    return ["repoze.lru"] if PY2 else []


setuptools.setup(
    name="paka.vx1",
    version="2.2.3",
    packages=setuptools.find_packages(),
    install_requires=_get_install_requirements(),
    extras_require={"testing": _get_testing_requirements()},
    include_package_data=True,
    namespace_packages=["paka"],
    zip_safe=False,
    url="https://github.com/PavloKapyshin/paka.vx1",
    keywords="blog generator static",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"],
    license="BSD",
    author="Pavlo Kapyshin",
    author_email="i@93z.org")
