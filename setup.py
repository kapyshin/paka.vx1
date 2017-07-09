import setuptools


def _get_install_requirements():
    requirements = [
        "mako", "markupsafe", "pygments", "lxml", "paka.cmark",
        "paka.feedgenerator", "paka.webstatic", "paka.breadcrumbs"]
    return requirements


setuptools.setup(
    name="paka.vx1",
    description="Static blog generator.",
    version="3.0.2",
    packages=setuptools.find_packages(),
    install_requires=_get_install_requirements(),
    extras_require={"testing": []},
    include_package_data=True,
    namespace_packages=["paka"],
    zip_safe=False,
    url="https://github.com/PavloKapyshin/paka.vx1",
    keywords="blog generator static",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython"],
    license="BSD",
    author="Pavlo Kapyshin",
    author_email="i@93z.org")
