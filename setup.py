from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in customer_side_app/__init__.py
from customer_side_app import __version__ as version

setup(
	name="customer_side_app",
	version=version,
	description="app for customer",
	author="basit",
	author_email="customer_app@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
