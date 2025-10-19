{ pkgs }:

pkgs.python3Packages.buildPythonApplication {
    pname = "elk";
    version = "0.1.0";
    pyproject = true;

    build-system = with pkgs.python3Packages; [ setuptools ];
    propagatedBuildInputs = [ ];

    src = ./.;
}