from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'CLI tools'
LONG_DESCRIPTION = 'Command Line tools'

# Setting up
setup(
    # the name must match the folder name ''
    name="cli-tools",
    version=VERSION,
    author="Pedro Mayorga",
    author_email="ppmayorga80@gmail.com",
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "colorama", "docopt", "pandas", "Pillow", "PyAutoGUI", "requests", "smart-open", "tabulate", "tqdm"
    ],  # add any additional packages that
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pycat = pycat:main',
            'pyhead = pyhead:main',
            'pytail = pytail:main',
            'pytab = pytab:main',
            'pywc = pywc:main',
            'pyqr = pyqr:main',
            'img2aa = img2aa:main',
            'ro3 = ro3:main',
            'xlscat = xlscat:main',
            'tout = tout:main',
            'arxiv = arxiv:main',
            'mr = mr:main',
        ],
    },
    # needs to be installed along with your package. Eg: 'caer'
    keywords=['python', 'cli tools'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Linux :: Linux",
        "Operating System :: Microsoft :: Windows",
    ])
