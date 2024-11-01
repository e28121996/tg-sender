{ pkgs }: {
  deps = [
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.python312Packages.flask
    pkgs.python312Packages.telethon
    pkgs.python312Packages.python-dotenv
  ];
}