from setuptools import setup, find_packages


__version__ = "0.0.1"

setup(
	name="curses_browser",
    version=__version__,
	packages=find_packages(),
	entry_points="""
	[console_scripts]
	cursesbrowser=curses_browser:viewer.main"""
)
