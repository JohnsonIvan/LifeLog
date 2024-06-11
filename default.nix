{ pkgs ? import <nixpkgs> {} }:
pkgs.python3Packages.callPackage ./lifelogserver.nix {}
