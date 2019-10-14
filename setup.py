from setuptools import setup, find_packages
 
setup(name='class_cli',
      version='0.1.4',
      url='https://github.com/yoavhayun/CLI',
      license='GNU General Public License v3.0',
      author='Yoav Hayun',
      author_email='yoavhayun@gmail.com',
      description='Converts a python class into a CLI program',
      packages=find_packages(),
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      zip_safe=False,
      install_requires=['prompt_toolkit>=2.0'],
      python_requires='>=3.0'
)