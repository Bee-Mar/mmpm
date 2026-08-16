{
  description = "MMPM: MagicMirror Package Manager";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    systems.url = "github:nix-systems/default";
    git-hooks.url = "github:cachix/git-hooks.nix";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    bun2nix = {
      url = "github:nix-community/bun2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      systems,
      git-hooks,
      uv2nix,
      bun2nix,
      pyproject-nix,
      pyproject-build-systems,
    }:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
      version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project.version;
      name = "mmpm";
    in
    {

      # ---- Git Hooks
      checks = forEachSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ bun2nix.overlays.default ];

          };
        in
        {
          pre-commit-check = git-hooks.lib.${system}.run {
            src = ./.;

            hooks = with pkgs; {
              py-format-src = {
                enable = true;
                name = "python:format";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff format mmpm tests";
              };

              py-sort-imports = {
                enable = true;
                name = "python:isort";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff check --select I --fix mmpm tests";
              };

              py-lint = {
                enable = true;
                name = "python:lint";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff check --fix mmpm tests";
              };

              ui-format = {
                enable = true;
                name = "ui:format";
                types = [
                  "javascript"
                  "ts"
                  "jsx"
                  "tsx"
                ];
                stages = [ "pre-commit" ];
                entry = "${bun}/bin/bun --cwd=ui run format";
              };

              ui-lint = {
                enable = true;
                pass_filenames = true;
                name = "ui:lint";
                types = [
                  "javascript"
                  "ts"
                ];
                stages = [ "pre-commit" ];
                entry = "${bun}/bin/bun --cwd=ui run lint";
              };

              ui-test = {
                enable = true;
                pass_filenames = false;
                name = "ui:test";
                types = [
                  "javascript"
                  "ts"
                  "jsx"
                  "tsx"
                ];
                stages = [ "pre-commit" ];
                entry = "CHROME_BIN=${chromium}/bin/chromium ${bun}/bin/bun --cwd=ui run test --watch=false --browsers=ChromeHeadlessNoSandbox";
              };

              nixfmt.enable = true;

              sync-version = {
                enable = true;
                name = "sync:version";
                stages = [ "pre-commit" ];
                pass_filenames = false;
                entry = toString (
                  pkgs.writeShellScript "sync-version" ''
                    set -euo pipefail
                    VERSION=$(${pkgs.python3}/bin/python3 -c "import tomllib; f=open('pyproject.toml','rb'); print(tomllib.load(f)['project']['version'])")
                    IFS='.' read -r MAJOR MINOR PATCH <<< "''${VERSION}"
                    printf '%s\n' \
                      "major = ''${MAJOR}" \
                      "minor = ''${MINOR}" \
                      "patch = ''${PATCH}" \
                      "" \
                      'version = f"{major}.{minor}.{patch}"' \
                      > mmpm/__version__.py
                    ${pkgs.gnused}/bin/sed -i \
                      "s/\"version\": \"[^\"]*\"/\"version\": \"''${VERSION}\"/" \
                      ui/package.json
                    git add mmpm/__version__.py ui/package.json
                  ''
                );
              };
            };
          };
        }
      );

      # ---- Packages
      packages = forEachSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ bun2nix.overlays.default ];
          };

          # ---- User Interface

          ui = pkgs.stdenv.mkDerivation {
            pname = "mmpm-ui";
            version = version;

            src = ./ui;

            nativeBuildInputs = [
              pkgs.bun2nix.hook
              # a real node is required in PATH: without it, bun executes ng.js itself and
              # reports its emulated Node version, which Angular CLI 22+ rejects as too old
              pkgs.nodejs_24
            ];

            bunDeps = pkgs.bun2nix.fetchBunDeps {
              bunNix = ./ui/bun.nix;
            };

            buildPhase = ''
              bun run build-prod
            '';

            installPhase = ''
              mkdir -p $out/ui
              cp -r build/browser/* $out/ui
            '';
          };

          inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;

          lib = pkgs.lib;

          projectName = name;
          python = pkgs.python313;

          # ---- MMPM CLI

          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          pyOverlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          mmpmOverlay = self: prev: {
            ${projectName} = prev.${projectName}.overrideAttrs (old: {
              propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [
                pkgs.pm2
              ];

              # Ensure ui is available in the scope
              buildInputs = (old.buildInputs or [ ]) ++ [ ui ];

              # Match deploy script; place files into the package source in site-packages
              # Use python.sitePackages to ensure path accuracy
              postInstall = (old.postInstall or "") + ''
                mkdir -p $out/${python.sitePackages}/mmpm/ui
                cp -r ${ui}/ui/* $out/${python.sitePackages}/mmpm/ui/
              '';
            });
          };

          # apply the overlay to the pythonSet
          pythonSet = (pkgs.callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              pyOverlay
              mmpmOverlay # inject UI like the `deploy` output
            ]
          );

          # Create the application using the modified pythonSet
          cli = mkApplication {
            # workspace.deps.default resolves 'mmpm' to the overridden version
            venv = pythonSet.mkVirtualEnv "mmpm-venv-${version}" workspace.deps.default;
            package = pythonSet.${projectName};
          };

          # ---- Utility Scripts
          start = pkgs.writeShellScriptBin "start" "pm2 start dev/ecosystem.json";
          stop = pkgs.writeShellScriptBin "stop" "pm2 stop mmpm";
          remove = pkgs.writeShellScriptBin "remove" "pm2 delete mmpm";
          logs = pkgs.writeShellScriptBin "logs" "pm2 logs mmpm";

          unit-tests = pkgs.writeShellScriptBin "unit-tests" ''
            uv run coverage run -m pytest
            CHROME_BIN=${pkgs.chromium}/bin/chromium bun --cwd=ui run test --watch=false --browsers=ChromeHeadlessNoSandbox
          '';
          static-analysis = pkgs.writeShellScriptBin "static-analysis" "uv run mypy mmpm";

          format = pkgs.writeShellScriptBin "format" ''
            uv run ruff format mmpm tests
            uv run ruff check --select I --fix mmpm tests
            bun --cwd=ui run format
          '';

          lint = pkgs.writeShellScriptBin "lint" ''
            uv run ruff check mmpm tests
            bun --cwd=ui run lint
          '';

          setup = pkgs.writeShellScriptBin "setup" ''
            uv sync --all-groups
            bun --cwd=ui install
          '';

          lock = pkgs.writeShellScriptBin "lock" ''
            uv lock --upgrade
            bun --cwd=ui update
            (cd ui && ${bun2nix.packages.${system}.default}/bin/bun2nix -o bun.nix)
          '';

          deploy = pkgs.writeShellScriptBin "deploy" ''
            cd ui
            bun run build-prod
            cd ..
            mkdir -p mmpm/ui
            cp -r ui/build/browser/* mmpm/ui
            uv sync
            uv build
          '';

          b2n = pkgs.writeShellScriptBin "b2n" ''
            ${bun2nix.packages.${system}.default}/bin/bun2nix -o bun.nix
          '';

        in
        {
          inherit
            cli
            ui
            start
            stop
            remove
            logs
            unit-tests
            static-analysis
            format
            lint
            setup
            lock
            deploy
            b2n
            ;

          default = cli;
        }
      );

      # ---- Dev Shell
      devShells = forEachSystem (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          scripts = with self.packages.${system}; [
            start
            stop
            remove
            logs
            unit-tests
            static-analysis
            format
            lint
            setup
            lock
            deploy
            b2n
          ];
        in
        {
          default = pkgs.mkShell {
            env = {
              UV_PYTHON = "3.14";
              VIRTUAL_ENV = ".venv";
            };

            packages =
              with pkgs;
              [
                uv
                bun
                pm2
                cacert
                chromium
                bun2nix.packages.${system}.default
              ]
              ++ scripts;

            shellHook = ''
              ${self.checks.${system}.pre-commit-check.shellHook}

              export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";

              [ ! -d $VIRTUAL_ENV ] && echo "Creating virtualenv ..." && uv venv

              source $VIRTUAL_ENV/bin/activate
              uv sync
              bun --cwd=ui install --ignore-scripts
            '';
          };
        }
      );
    };
}
