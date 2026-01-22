# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 22 May 2025

# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace

{ pkgs, ... }: {
  channel = "stable-24.05";
  # Use https://search.nixos.org/packages to find packages
  packages = with pkgs; [
    gitflow
    git-lfs
    oh-my-posh
    python312
    nodePackages.vercel
  ];
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "adpyke.codesnap"
      "akamud.vscode-theme-onedark"
      "augustocdias.tasks-shell-input"
      "DavidAnson.vscode-markdownlint"
      "detachhead.basedpyright"
      "eamodio.gitlens"
      "grapecity.gc-excelviewer"
      "mechatroner.rainbow-csv"
      "mermaidchart.vscode-mermaid-chart"
      "mhutchie.git-graph"
      "ms-python.flake8"
      "ms-python.python"
      "ms-toolsai.jupyter"
      "samuelcolvin.jinjahtml"
      "waderyan.gitblame"
      "yzhang.markdown-all-in-one"
    ];
    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "vercel"
            "dev"
            "--listen"
            "127.0.0.1:$PORT"
          ];
          manager = "web";
        };
      };
    };
    workspace.onStart.default.openFiles = [
      "README.md"
    ];
  };
}
