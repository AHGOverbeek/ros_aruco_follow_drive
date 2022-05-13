from setuptools import setup

package_name = 'ros_aruco_follow_drive'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mark',
    maintainer_email='m.vlutters@utwente.nl',
    description='EVE drive commands based on ARUCO info',
    license='Apache2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "ros_aruco_follow_drive = ros_aruco_follow_drive.aruco_driver:main"
        ],
    },
)
