{ pkgs }: {
    deps = [
        # Python base
        pkgs.python310
        pkgs.python310Packages.pip
        pkgs.python310Packages.setuptools
        
        # Required for Telethon
        pkgs.openssl
        pkgs.cacert
        
        # System dependencies
        pkgs.which
        pkgs.tree
        pkgs.git
    ];
}