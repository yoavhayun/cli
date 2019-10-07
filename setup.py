from setuptools import setup, find_packages
 
setup(name='class_cli',
      version='0.1',
      url='https://github.com/yoavhayun/CLI',
      license='GNU General Public License v3.0',
      author='Yoav Hayun',
      author_email='yoavhayun@gmail.com',
      description='Converts a python class into a CLI program',
      packages=find_packages(),
      long_description=open('README.md').read(),
      zip_safe=False,
      setup_requires=['prompt_toolkit>=2.0'])