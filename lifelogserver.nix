{
	lib,
	buildPythonPackage,
	flask,
	setuptools,
	wheel,
	packaging,
	waitress,
	matplotlib,
	numpy,

	...
}:

buildPythonPackage rec {
	pname = "lifelogserver";
	version = "0.0.1";

	src = ./src;

	build-system = [
		setuptools
		wheel
	];

	propagatedBuildInputs = [
		flask
		setuptools
		wheel
		packaging
		waitress
		matplotlib
		numpy
	];

	doCheck = false;

	#pythonImportsCheck = [
	#	"toolz.itertoolz"
	#	"toolz.functoolz"
	#	"toolz.dicttoolz"
	#];
}
