from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    long_description = ''.join(f.readlines())

setup(
    name='wrpclient',
    version='0.1',
    description='Workswell Remote Protocol Client',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Petr Kasalický',
    author_email='kasape@atlas.cz',
    keywords='thermal, infrared, camera, workswell, remote, protocol, client',
    license='GNU GPLv3 License',
    url='https://github.com/Kasape/wrpclient',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: IPython',
        'Framework :: AsyncIO'
        ],
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=['numpy'],
)
