from setuptools import find_packages, setup

setup(
    name="zoom-oauth-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click", "pyngrok", "requests"],
    entry_points={"console_scripts": ["zoom-oauth-cli = zoom_oauth_cli:cli"]},
)
