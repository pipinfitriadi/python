# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 22 May 2025

# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace

{}: {
  channel = "stable-24.05";
  idx = {
    extensions = [
      "mhutchie.git-graph"
    ];
  };
}
