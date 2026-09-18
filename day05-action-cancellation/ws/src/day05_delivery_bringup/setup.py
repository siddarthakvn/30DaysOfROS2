from setuptools import setup

package_name = "day05_delivery_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="kvn",
    maintainer_email="kvn@example.com",
    description="Day 05 warehouse delivery action server and operator client.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "delivery_server = day05_delivery_bringup.delivery_server:main",
            "delivery_client = day05_delivery_bringup.delivery_client:main",
        ],
    },
)
