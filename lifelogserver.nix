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
	version = "0.0.1"; # TODO: de-dupe. Somehow. Or at least write a unit test?

	src = ./src;

	build-system = [
		flask
		setuptools
		wheel
		packaging
		waitress
		matplotlib
		numpy
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

	doCheck = true;

	#pythonImportsCheck = [
	#	"toolz.itertoolz"
	#	"toolz.functoolz"
	#	"toolz.dicttoolz"
	#];
}
