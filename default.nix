let
	pkgs = import <nixpkgs> {};
	lls = import ./derivation.nix {
		inherit pkgs;
		python3Packages = pkgs.python3Packages;
	};
in pkgs.mkShell {
	packages = [
		lls
	];
}
