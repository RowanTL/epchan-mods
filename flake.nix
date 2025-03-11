{
  description = "A flake for developing in a clojure environment with vscode";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
  };

  outputs = { nixpkgs, ... }:
  let system = "x86_64-linux"; in
  {
    devShells."${system}".default =
    let
      pkgs = nixpkgs.legacyPackages."${system}";
    in
      pkgs.mkShellNoCC {
        buildInputs = [ pkgs.bashInteractive ];
        packages = with pkgs; [
          (python3.withPackages (pypkgs: [
            pypkgs.pandas
            pypkgs.polars
            pypkgs.matplotlib
            pypkgs.numpy
            pypkgs.jupyter
            pypkgs.pip
            pypkgs.notebook
            pypkgs.xlrd
            pypkgs.statsmodels
            pypkgs.jupyterlab
            pypkgs.ipykernel
            pypkgs.pyzmq
          ]))
          zeromq
          (vscode-with-extensions.override {
            vscode = vscodium;
            vscodeExtensions = with vscode-extensions; [
              ms-python.python
              ms-azuretools.vscode-docker
              ms-toolsai.datawrangler
              ms-toolsai.jupyter
              eamodio.gitlens
              bbenoist.nix
              mechatroner.rainbow-csv
              donjayamanne.githistory
              # pkgs.vscode-utils.extensionsFromVscodeMarketplace [
              # {
              #   name = "calva";
              #   publisher = "betterthantomorrow";
              #   version = "v2.0.486";
              #   sha256 = "sha256-pL+OgJvIK5eqE5Kr/wDeJ+2BGUT9Uj42coWSHtbPolk=";
              # }
            ];
          })
        ];
        shellHook = ''
          export SHELL=${pkgs.lib.getExe pkgs.bashInteractive}
          echo "starting codium"
          codium .
        '';
      };
  };
}
