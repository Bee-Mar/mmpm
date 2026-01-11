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
      projectVersion = "4.2.5";
    in
    {

      # --------------------------------------------------------------------
      # CHECKS (pre-commit)
      # --------------------------------------------------------------------
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
                  "jsx"
                  "tsx"
                ];
                stages = [ "pre-commit" ];
                entry = "${bun}/bin/bun --cwd=ui run lint";
              };

              nixfmt.enable = true;
            };
          };
        }
      );

      # --------------------------------------------------------------------
      # PACKAGES
      # --------------------------------------------------------------------
      packages = forEachSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ bun2nix.overlays.default ];
          };

          lib = pkgs.lib;

          projectName = "mmpm";
          python = pkgs.python313;

          # ---- uv2nix (Python backend) ------------------------------------

          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          pyOverlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          pythonSet = (pkgs.callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              pyOverlay
            ]
          );

          cli = (
            pythonSet.${projectName}.overrideAttrs (old: {
              # If you already have postInstall or similar phase
              postInstall = (old.postInstall or "") + ''
                mkdir -p $out/${python.sitePackages}/mmpm/ui
                cp -r ${ui}/ui/* $out/${python.sitePackages}/mmpm/ui/
              '';
            })
          );

          # ---- bun2nix (UI) ------------------------------------------------

          ui = pkgs.stdenv.mkDerivation {
            pname = "mmpm-ui";
            version = projectVersion;

            src = ./ui;

            nativeBuildInputs = [
              pkgs.bun2nix.hook
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

          # ---- Utility scripts --------------------------------------------

          start = pkgs.writeShellScriptBin "start" ''pm2 start dev/ecosystem.json'';
          stop = pkgs.writeShellScriptBin "stop" ''pm2 stop mmpm'';
          remove = pkgs.writeShellScriptBin "remove" ''pm2 delete mmpm'';
          logs = pkgs.writeShellScriptBin "logs" ''pm2 logs mmpm'';

          unit-tests = pkgs.writeShellScriptBin "unit-tests" ''uv run coverage run -m pytest'';
          static-analysis = pkgs.writeShellScriptBin "static-analysis" ''uv run mypy mmpm'';

          format = pkgs.writeShellScriptBin "format" ''
            uv run ruff format mmpm tests
            uv run ruff check --select I --fix mmpm tests
            bun --cwd=ui run format
          '';

          lint = pkgs.writeShellScriptBin "lint" ''
            uv run ruff check mmpm
            bun --cwd=ui run lint
          '';

          setup = pkgs.writeShellScriptBin "setup" ''
            uv run ruff check mmpm
            bun --cwd=ui run lint
          '';

          lock = pkgs.writeShellScriptBin "lock" ''
            uv lock --upgrade
            bun --cwd=ui update
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
            ;

          default = cli;
        }
      );

      # ------------------------------------------------

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
          ];
        in
        {
          default = pkgs.mkShell {
            env = {
              UV_PYTHON = "3.13";
              SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";
              VIRTUAL_ENV = ".venv";
            };

            packages =
              with pkgs;
              [
                uv
                bun
                pm2
              ]
              ++ scripts;

            shellHook = ''
              ${self.checks.${system}.pre-commit-check.shellHook}

              [ ! -d $VIRTUAL_ENV ] && echo "Creating virtualenv ..." && uv venv

              source $VIRTUAL_ENV/bin/activate
              uv sync
              bun --cwd=ui install
            '';
          };
        }
      );
    };
}
