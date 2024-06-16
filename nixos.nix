{ config, pkgs, ... }:

let
	lls = import ./derivation.nix { inherit pkgs; };
in {
	config = {
		environment.systemPackages = with pkgs; [
			lls
		];

		users.groups.lls-wheel = {};

		users.users.lls = {
			isSystemUser = true;
			description = "User for the lls server";
			group = "lls-wheel";
		};
	};
}
