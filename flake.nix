{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    systems.url = "github:nix-systems/default";
    git-hooks.url = "github:cachix/git-hooks.nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      systems,
      git-hooks,
    }:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      checks = forEachSystem (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          pre-commit-check = git-hooks.lib.${system}.run {
            src = ./.;

            hooks = with pkgs; {
              py-format-src = {
                enable = true;
                name = "python:format";
                description = "Python formatting stage";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff format mmpm tests";
              };

              py-typing = {
                enable = false;
                name = "python:typing";
                description = "Python type checking stage";
                types = [ "python" ];
                stages = [ "pre-push" ];
                entry = "${uv}/bin/uv run mypy mmpm";
              };

              py-test = {
                enable = false;
                name = "python:test";
                description = "Python testing stage";
                types = [ "python" ];
                stages = [ "pre-push" ];
                entry = "${uv}/bin/uv run pytest";
              };

              py-sort-imports = {
                enable = true;
                name = "python:isort";
                description = "Python formatting stage";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff check --select I --fix mmpm tests";
              };

              py-lint = {
                enable = true;
                name = "python:lint";
                description = "Python linting stage";
                types = [ "python" ];
                stages = [ "pre-commit" ];
                entry = "${uv}/bin/uv run ruff check --fix mmpm tests";
              };

              ui-format = {
                enable = true;
                name = "ui:format";
                description = "UI linting stage";
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
                description = "UI linting stage";
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

      packages = forEachSystem (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          start = pkgs.writeShellScriptBin "start" ''pm2 start dev/ecosystem.json '';
          stop = pkgs.writeShellScriptBin "stop" ''pm2 stop mmpm '';
          remove = pkgs.writeShellScriptBin "remove" ''pm2 delete mmpm '';
          logs = pkgs.writeShellScriptBin "logs" ''pm2 logs mmpm '';

          unit-tests = pkgs.writeShellScriptBin "unit-tests" ''uv run coverage run -m pytest '';
          static-analysis = pkgs.writeShellScriptBin "static-analysis" ''uv run mypy mmpm '';

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
            bun install --legacy-peer-deps
            ./node_modules/@angular/cli/bin/ng.js build --configuration production --output-hashing none --base-href /
            cd ..
            mkdir -p mmpm/ui
            cp -r ui/build/browser/* mmpm/ui
            uv sync
            uv build
          '';
        }
      );

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
            env = with pkgs; {
              UV_PYTHON = "3.13";
              SSL_CERT_FILE = "${cacert}/etc/ssl/certs/ca-bundle.crt";
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

              [ ! -d $VIRTUAL_ENV ] && echo 'Creating virtualenv ...' && uv venv

              source $VIRTUAL_ENV/bin/activate
              uv sync

              bun --cwd=ui install
            '';

          };
        }
      );
    };
}
