"""
Setup script for ROI Calculator
Allows installation as a Python package
"""

from setuptools import setup, find_packages
import os

# Read long description from README
readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'ROI_Calculator_README.md')
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "E-commerce Operations ROI Calculator"

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name='roi-calculator',
    version='1.0.0',
    author='E-commerce Operations Consulting',
    author_email='info@ecommerce-ops.com',
    description='Comprehensive ROI calculator for e-commerce operations optimization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your-org/roi-calculator',
    
    # Package information
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Include additional files
    package_data={
        'roi_calculator': [
            '../templates/*.html',
            '../static/css/*.css',
            '../static/js/*.js',
            '../static/images/*'
        ]
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements('requirements.txt'),
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.812'
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0'
        ]
    },
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Classification
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Environment :: Web Environment',
    ],
    
    # Keywords for package discovery
    keywords='roi calculator ecommerce operations consulting chile business finance',
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'roi-calculator=cli_interface:main',
            'roi-calculator-web=web_interface:main',
            'roi-calc=run:main'
        ]
    },
    
    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/your-org/roi-calculator/blob/main/README.md',
        'Bug Reports': 'https://github.com/your-org/roi-calculator/issues',
        'Source': 'https://github.com/your-org/roi-calculator',
    },
    
    # Zip safe
    zip_safe=False,
)