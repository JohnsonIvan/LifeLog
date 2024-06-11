with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
	name = "lifelogserver";
	version = "0.0.1";

	src = ./src;

	propagatedBuildInputs = [
		pytest
		numpy
	];
}
