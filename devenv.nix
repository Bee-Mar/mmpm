{ pkgs, lib, config, inputs, ... }:
{
  # https://devenv.sh/basics/
  cachix.enable = false;

  env = {
    UV_PYTHON = "3.13";
  };

  # https://devenv.sh/packages/
  packages = with pkgs; [
    uv
    bun
    pm2
  ];

  # https://devenv.sh/languages/
  # https://devenv.sh/services/
  # https://devenv.sh/scripts/
  # https://devenv.sh/processes/

  enterShell = ''
    export VIRTUAL_ENV="$DEVENV_ROOT/.venv"

    [ -z $SSL_CERT_FILE ] && export SSL_CERT_FILE="/etc/ssl/certs/ca-bundle.crt"

    [ ! -d $VIRTUAL_ENV ] && echo 'Creating virtualenv ...' && uv venv

    source $VIRTUAL_ENV/bin/activate
    uv sync

    bun --cwd=$DEVENV_ROOT/ui install
  '';

  tasks = {
    "py:report".exec = "uv run coverage report";
    "py:test".exec = "uv run coverage run -m pytest";
    "py:typing".exec = "uv run mypy mmpm";
    "py:isort".exec = "uv run ruff check --select I --fix mmpm tests";
    "py:lint".exec = "uv run ruff check mmpm";

    "ui:build".exec = "bun --cwd=$DEVENV_ROOT/ui run build";
    "ui:start".exec = "bun --cwd=$DEVENV_ROOT/ui run start";
    "ui:lint".exec = "bun --cwd=$DEVENV_ROOT/ui run lint";

    "mmpm:format".exec = ''
      uv run ruff format mmpm tests
      uv run ruff check --select I --fix mmpm tests
      bun --cwd=$DEVENV_ROOT/ui run format
    '';

    "mmpm:lint".exec = ''
      uv run ruff check mmpm
      bun --cwd=$DEVENV_ROOT/ui run lint
    '';

    "mmpm:setup".exec = ''
      uv sync
      bun --cwd=$DEVENV_ROOT/ui install
    '';

    "mmpm:lock".exec = ''
      uv lock --upgrade
      bun --cwd=$DEVENV_ROOT/ui update
    '';

    "mmpm:start".exec = "pm2 start $DEVENV_ROOT/dev/ecosystem.json";
    "mmpm:stop".exec = "pm2 stop mmpm";
    "mmpm:rm".exec = "pm2 delete mmpm";
    "mmpm:logs".exec = "pm2 logs mmpm";

    "mmpm:deploy".exec = ''
      cd ui
      bun install --legacy-peer-deps
      ./node_modules/@angular/cli/bin/ng.js build --configuration production --output-hashing none --base-href /
      cd ..
      mkdir -p mmpm/ui
      cp -r ui/build/browser/* mmpm/ui
      uv sync
      uv build
    '';
  };

  # https://devenv.sh/tests/
  enterTest = ''
    uv run coverage run -m pytest
  '';

  # https://devenv.sh/git-hooks/
  git-hooks.hooks = {
    py-format-src = {
      enable = true;
      name = "python:format";
      description = "Python formatting stage";
      types = [ "python" ];
      stages = [ "pre-commit" ];
      entry = "${pkgs.uv}/bin/uv run ruff format mmpm tests";
    };

    py-typing = {
      enable = false;
      name = "python:typing";
      description = "Python type checking stage";
      types = [ "python" ];
      stages = [ "pre-push" ];
      entry = "${pkgs.uv}/bin/uv run mypy mmpm";
    };

    py-test = {
      enable = false;
      name = "python:test";
      description = "Python testing stage";
      types = [ "python" ];
      stages = [ "pre-push" ];
      entry = "${pkgs.uv}/bin/uv run pytest";
    };

    py-sort-imports = {
      enable = true;
      name = "python:isort";
      description = "Python formatting stage";
      types = [ "python" ];
      stages = [ "pre-commit" ];
      entry = "${pkgs.uv}/bin/uv run ruff check --select I --fix mmpm tests";
    };

    py-lint = {
      enable = true;
      name = "python:lint";
      description = "Python linting stage";
      types = [ "python" ];
      stages = [ "pre-commit" ];
      entry = "${pkgs.uv}/bin/uv run ruff check --fix mmpm tests";
    };

    ui-format = {
      enable = true;
      name = "ui:format";
      description = "UI linting stage";
      types = [ "javascript" "ts" "jsx" "tsx" ];
      stages = [ "pre-commit" ];
      entry = "${pkgs.bun}/bin/bun --cwd=$DEVENV_ROOT/ui run format";
    };

    ui-lint = {
      enable = true;
      pass_filenames = true;
      name = "ui:lint";
      description = "UI linting stage";
      types = [ "javascript" "ts" "jsx" "tsx" ];
      stages = [ "pre-commit" ];
      entry = "${pkgs.bun}/bin/bun --cwd=$DEVENV_ROOT/ui run lint";
    };
  };

  # See full reference at https://devenv.sh/reference/options/
}
