#!/bin/bash
set -e
DISTDIR=/home/jeremy/Desktop/output/dist/SpeeDReaD/SpeeDReaD
PROGRAMNAME=speedread
FRIENDLYNAME="SpeeDReaD"
EXECNAME=SpeeDReaD
VERSION=2.1.3.001
ICONLOCATION=_internal/resources/sr_logo.png
ICON=sr_logo.png
CONTROLSECTION=utils
DEPENDENCIES="python3, libxcb-cursor0, libwayland-cursor0, menu, desktop-file-utils"
DESCRIPTION="Speed Reading Program"
MENUSECTION=Applications/Education
TYPE=Application
CATEGORIES="Education"

if test -d "$DISTDIR/$PROGRAMNAME.$VERSION"; then
    echo Deleting Old Build Directory
    rm -rf "$DISTDIR/$PROGRAMNAME.$VERSION"
fi

echo Creating Directories
mkdir -p "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN"
mkdir -p "$DISTDIR/$PROGRAMNAME.$VERSION/usr/local/$PROGRAMNAME"
mkdir -p "$DISTDIR/$PROGRAMNAME.$VERSION/usr/share/applications"
mkdir -p "$DISTDIR/$PROGRAMNAME.$VERSION/usr/share/icons/hicolor/scalable/apps"

echo Creating control File
cat > "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/control" <<EOF
Package: $PROGRAMNAME
Version: $VERSION
Section: $CONTROLSECTION
Priority: optional
Architecture: all
Replaces: $PROGRAMNAME (<< $VERSION)
Depends: $DEPENDENCIES
Maintainer: Jeremy Wilson pastorjeremywilson@gmail.com
Homepage: https://pastorjeremywilson.github.io
Description: $DESCRIPTION

EOF

echo Creating menu File
cat > "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/$PROGRAMNAME.menu" <<EOF
Package($PROGRAMNAME): \
    Section="$MENUSECTION" \
    Title="$FRIENDLYNAME" \
    Command="/usr/local/$PROGRAMNAME/$EXECNAME" \
    Icon="/usr/share/icons/hicolor/scalable/apps/$ICON"
EOF

echo Creating desktop File
cat > "$DISTDIR/$PROGRAMNAME.$VERSION/usr/share/applications/$PROGRAMNAME.desktop" <<EOF
[Desktop Entry]
StartupWMClass=$FRIENDLYNAME
Version=1.0
Exec=/usr/local/$PROGRAMNAME/$EXECNAME
Comment=$DESCRIPTION
Terminal=false
PrefersNonDefaultGPU=false
Icon=/usr/share/icons/hicolor/scalable/apps/$ICON
Type=$TYPE
Name=$FRIENDLYNAME
Categories=$CATEGORIES;

EOF
chmod +x "$DISTDIR/$PROGRAMNAME.$VERSION/usr/share/applications/$PROGRAMNAME.desktop"

echo Copying Program Data
cp "$DISTDIR/$EXECNAME" "$DISTDIR/$PROGRAMNAME.$VERSION/usr/local/$PROGRAMNAME"
cp -r "$DISTDIR/_internal" "$DISTDIR/$PROGRAMNAME.$VERSION/usr/local/$PROGRAMNAME"
cp "$DISTDIR/$ICONLOCATION" "$DISTDIR/$PROGRAMNAME.$VERSION/usr/share/icons/hicolor/scalable/apps/$ICON"
chmod +x "$DISTDIR/$PROGRAMNAME.$VERSION/usr/local/$PROGRAMNAME"

echo Creating postinst File
cat > "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/postinst" <<EOF
#!/bin/bash
set -e
if [ -x /usr/bin/update-icon-caches ]; then
    update-icon-caches /usr/share/icons/hicolor
fi
if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database /usr/share/applications
fi
EOF
chmod 0555 "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/postinst"

echo Creating postrm File
cat > "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/postrm" <<EOF
#!/bin/sh
set -e
if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database /usr/share/applications
fi
EOF
chmod 0555 "$DISTDIR/$PROGRAMNAME.$VERSION/DEBIAN/postrm"

echo Building .deb File
sudo dpkg-deb --build "$DISTDIR/$PROGRAMNAME.$VERSION"

if [[ $# -eq 0 ]] || [[ $1 != "-k" && $1 != "--keep-build-dir" ]]; then
    echo Deleting Build Directory
    rm -rf "$DISTDIR/$PROGRAMNAME.$VERSION"
fi
