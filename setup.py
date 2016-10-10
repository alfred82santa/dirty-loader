from setuptools import setup
import os

setup(
    name='dirty-loader',
    url='https://github.com/alfred82santa/dirty-loader',
    author='alfred82santa',
    version='0.2.2',
    license='LGPLv2.1',
    author_email='alfred82santa@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'],
    packages=['dirty_loader'],
    include_package_data=False,
    install_requires=[],
    description="Dirty loader for python 3",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    test_suite="nose.collector",
    tests_require="nose",
    zip_safe=True,
)
