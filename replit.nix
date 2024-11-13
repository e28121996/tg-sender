{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.flask
    pkgs.python310Packages.telethon
    pkgs.python310Packages.python-dotenv
  ];
}