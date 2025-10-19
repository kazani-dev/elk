{
  description = "A program for managing a local store for ephemeral directories nested in network resources.";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];
      perSystem = { config, self', inputs', pkgs, system, ... }: {
        packages.elk = pkgs.python3Packages.buildPythonApplication {
          pname = "elk";
          version = "0.1.0";
          pyproject = true;

          build-system = [ pkgs.python3Packages.setuptools ];
          propagatedBuildInputs = [ ];

          src = ./.;
        };

        packages.default = config.packages.elk;
      };
    };
}
