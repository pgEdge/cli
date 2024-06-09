#! /bin/bash
cd "$(dirname "$0")"

source ../../env.sh

cd $OUT

#This script generates an RPM or DEB package.

#Input: Directory containing appropriate pg binaries tar.gz.
#Output: RPM in ~/pgedge_build/RPMS/x86_64
#        DEB in ~/pgedge_build

HELP_TEXT() {
    printf "\n"
    printf "  Required Flags:\n"
    printf "      --major_ver <16>\n"
    printf "          Specify a PostgreSQL Major Version Number\n"
    printf "      --minor_ver <3>\n"
    printf "          Specify a PostgreSQL Minor Version Number\n"
    printf "      --release <1>\n"
    printf "          Specify an internal Release Number\n"
    printf "      --bundle_name <bundle-pg16.3.1-edge24.7.0-el9>\n"
    printf "          Specify the package bundle name\n"

    printf "\n"
}


exit_error_msg () {
    printf "\n"
    printf "ERROR: $1\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
}




# Default options
MIRROR_URL="http://localhost:8000/"
SOURCE_DIR="/tmp"
while [ -n "$1" ] 
do
    case "$1" in
    --major_ver | -majorver ) 
            shift
            MAJOR_VER="$1"
            shift
            ;;
    --minor_ver | -minorver )
            shift
            MINOR_VER="$1"
            shift
            ;;
    --release | -r ) 
            shift
            RELEASE="$1"
            shift
            ;;
    --bundle_name ) 
            shift
            BUNDLE_NAME="$1"
            shift
            ;;
    --help | -h | -? ) 
            printf " $0 \n"
            HELP_TEXT
            exit 1
            ;;
	* )
	   printf "Invalid option: $1\n"
	   exit 1
           ;;
    esac
done
###############################################

#VARS_STRING="$MAJOR_VER $MINOR_VER $RELEASE $RPM_RELEASE $PKG_NAME $SOURCE_DIR $INIT_SCRIPT_SRC $SYSTEMD_SCRIPTS "

#VAR_NUM="$VARS_STRING | wc -w"

if [ -z "$MAJOR_VER" ]; then
    exit_error_msg "Must set --major_ver"
elif [ -z "$MINOR_VER" ]; then
    exit_error_msg "Must set --minor_ver"
elif [ -z "$RELEASE" ]; then
    exit_error_msg "Must set --release"
elif [ -z "$BUNDLE_NAME" ]; then
    exit_error_msg "Must set --bundle_name"
fi

#PKG_NAME="$PKG_NAME${MAJOR_VER//[.]/}"
#PG_NAME="postgresql${MAJOR_VER//[.]/}"
#SANDBOX_NAME="pgedge-$MAJOR_VER.$MINOR_VER-$RELEASE.tar.bz2"

echo 
echo ## Locating Package Bundle File ###################

bundle_tgz=$BUNDLE_NAME.tgz
if [ ! -f $bundle_tgz ]; then
    fatalError "Input file not found \"$bundle_tgz\""
fi


echo 
echo ## PostgreSQL RPM/DEB generation script ###########

#This variable is used to determine value for LD_PRELOAD, a fix for psql dumb terminal issue.
LIBREADLINE_SEARCH_PATH="/lib"

# Determine architecture where script is running to determine appropriate
# binary tar.gz names.
ARCH=`uname -i`
if [ "$ARCH" = "unknown" ];
then 
  ARCH=`uname -m`
fi

echo "Platform: $ARCH"
if [ $ARCH = "x86_64" ]; then
  OS_PLATFORM="linux-x64"
  DEBIAN_ARCH=amd64
  LIBREADLINE_SEARCH_PATH="/lib64"
fi

DEBIAN_ARCH=x64

INSTALLATION_PATH="/opt/pgedge"
PGINSTALLATION_PATH="$INSTALLATION_PATH/pg`echo $MAJOR_VER | sed 's/\.//g'`"
PG_LINUX_TAR="$SOURCE_DIR/pgedge-$MAJOR_VER.$MINOR_VER-$RELEASE-linux64.tar.bz2"
TMP_PREFIX="/tmp/PG_PGEDGE_BUILD"
TMP_ROOT="$TMP_PREFIX$INSTALLATION_PATH"
TMP_INITD="$TMP_ROOT/pg`echo $MAJOR_VER | sed 's/\.//g'`/startup"
INITD="postgresql-`echo $MAJOR_VER | sed 's/\.//g'`"
PG_BUILD_DIR_NAME="pg_pgedge_build"
PG_TRANSFORMED_TAR="/tmp/$PKG_NAME-$MAJOR_VER.$MINOR_VER-$RPM_RELEASE-$OS_PLATFORM-pgedge.tar.gz"
ENVFILE_NAME="pg${MAJOR_VER//[.]/}.env"
ENVFILE="$TMP_ROOT/$ENVFILE_NAME"
DEBIAN_DIR="pgedge-$MAJOR_VER.$MINOR_VER-$RELEASE-$DEBIAN_ARCH"
RPMOSUSER="pgedge"
###################################################################

function convertToPackageFriendly {
  # Convert to rpm friendly tar.gz
  echo "Converting to rpm friendly tar.gz..."
  if [ -f $PG_LINUX_TAR ];
  then
	 rm -rf $TMP_PREFIX
	 mkdir -p $TMP_ROOT
	 #tar -xzf $PG_LINUX_TAR -C $TMP_ROOT
	 #tar -xf $PG_LINUX_TAR -C $TMP_ROOT
     tar -xf $PG_LINUX_TAR -C $TMP_ROOT --strip 1
         #Remove stuff that we don't require
	 mv $TMP_ROOT/pg${MAJOR_VER//[.]/}-$MAJOR_VER.$MINOR_VER-$RELEASE-linux64/* $TMP_ROOT
	 rm -r $TMP_ROOT/pg${MAJOR_VER//[.]/}-$MAJOR_VER.$MINOR_VER-$RELEASE-linux64
	 #rm -rf $TMP_ROOT/stackbuilder
	 #rm -rf $TMP_ROOT/pgAdmin3
	 rm -f $PG_TRANSFORMED_TAR
#	 touch $ENVFILE 
	 #Dump default environment values
#	 cat <<ENVEOF > $ENVFILE 
##!/bin/bash
#export PGHOME=$INSTALLATION_PATH/pg${MAJOR_VER//[.]/}
#export PGDATA=$INSTALLATION_PATH/data/pg${MAJOR_VER//[.]/}
#export PATH=$INSTALLATION_PATH/pg${MAJOR_VER//[.]/}/bin:\$PATH
#export LD_LIBRARY_PATH=$INSTALLATION_PATH/pg${MAJOR_VER//[.]/}/lib:\$LD_LIBRARY_PATH
#export PGUSER=postgres
#export PGDATABASE=postgres
#ENVEOF
#	 chmod 777 $ENVFILE
	 #Creating init.d script
	 #createInitScript 
	 tar -czf $PG_TRANSFORMED_TAR -C $TMP_PREFIX opt
else
	 echo $PG_LINUX_TAR not found.
	 exit 1
fi

}

function createRPMBuildStructure {
  echo "Creating rpm build structure..."
  rm -rf ~/$PG_BUILD_DIR_NAME
  mkdir -p ~/$PG_BUILD_DIR_NAME/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}

  if [ -f ~/.rpmmacros ];
  then
    echo "Creating .rpmmacros backup..."
    cp ~/.rpmmacros ~/.rpmmacros.oscg.bak
    echo "Overwriting ~/.rpmmacros"
  else
    echo "Creating ~/.rpmmacros"  
  fi

  cat <<EOF> ~/.rpmmacros
%_topdir   %(echo $HOME)/$PG_BUILD_DIR_NAME
%_tmppath  %{_topdir}/tmp
%_signature gpg
%_gpg_name PGEDGE
EOF
}
function createRPMSpec {
  echo "Preparing rpm sources..."
  if [ -f $PG_TRANSFORMED_TAR ];
  then
	 cp $PG_TRANSFORMED_TAR ~/$PG_BUILD_DIR_NAME/SOURCES/
  fi

  echo "Creating spec file..."
  SPEC_OUTPUT="$PG_BUILD_DIR_NAME/SPECS/$PKG_NAME-$MAJOR_VER.$MINOR_VER-$OS_PLATFORM-pgedge.spec"

  FILES=$(/bin/tar -tzf $PG_TRANSFORMED_TAR | /bin/grep -v '^.*/$' | sed 's/^/\//')
  DIRS=$(/bin/tar -tvzf $PG_TRANSFORMED_TAR | grep "^d" | awk '{ print $6 }' | sed 's/^/\//' | sort | uniq)
#echo $DIRS
  FULL_VERSION="$MAJOR_VER.$MINOR_VER"
/bin/cat > ~/$SPEC_OUTPUT << EOF
%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress
%define        __prelink_undo_cmd ${nil}

Name: $PKG_NAME
Version: $FULL_VERSION
Release: $RPM_RELEASE
Vendor: PGEDGE
Summary: PostgreSQL RPM by PGEDGE
License: pgEdge Community License v1.0
Group: Applications/Databases
Source0: %{name}-%{version}-%{release}-$OS_PLATFORM-pgedge.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: $ARCH
URL: http://pgedge.com
Prefix: $INSTALLATION_PATH
%description
PostgreSQL by PGEDGE

%prep
%setup -c -n %{name}-%{version}
#Custom find_require to exclude libjvm and libtcl
%{__cat} > find_requires.sh << FR_EOF
#!/bin/sh
exec %{__find_requires} | egrep -v 'libjvm.so|libodbc|libR.so|libclntsh.so.10|libsybdb.so.5|libcassandra.so.2|libbson|libmongoc|libpython|dtrace|libevent|libperl|libtcl|GLIBC_2.13'
#exec %{__find_requires} | egrep -v 'libjvm.so|libodbc|libR.so|libclntsh.so.10|libsybdb.so.5|libcassandra.so.2|libbson|libmongoc|dtrace|libevent'
exit 0
FR_EOF
chmod +x find_requires.sh
%define _use_internal_dependency_generator 0
%define __find_requires %{_builddir}/%{name}-%{version}/find_requires.sh

%build
#Empty Section

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a opt %{buildroot} 
#cp -a etc %{buildroot} 

%pre
#Empty Section

if [ "\$1" -eq "2" ]
then
    printf "\n\n=====  UPGRADE FAILURE ================\n"
    exit 1
fi

%post
ln -s \$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}/bin/psql /usr/bin/psql 2>/dev/null
ln -s \$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}/lib/libpq.so.5 /usr/lib64/libpq.so.5 2>/dev/null

cat <<ENVEOF > \$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}.env
#!/bin/bash
export PGHOME=\$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}
export PGDATA=\$RPM_INSTALL_PREFIX/data/pg${MAJOR_VER//[.]/}
export PATH=\$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}/bin:\$PATH
export LD_LIBRARY_PATH=\$RPM_INSTALL_PREFIX/pg${MAJOR_VESION//[.]/}/lib:\$LD_LIBRARY_PATH
export PGUSER=postgres
export PGDATABASE=postgres
ENVEOF

chmod 0755 \$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}.env

printMessage=1
# 2 means we're performing an upgrade
if [ "\$1" = "2" ]
then
    # If the env file exists, we're doing an upgrade of an initialized system
    if [ -f \$RPM_INSTALL_PREFIX/pg${MAJOR_VER//[.]/}.env ]
    then
        printf "\n\tMinor Version update completed, please restart\n"
        printf "\t the server for changes to take effect\n\n"
        printMessage=0
    fi
fi
if [ "\$printMessage" -eq 1 ]
then
    # Post installation actions
    printf "\n\t======================================\n"
    printf "\tBinaries installed at: \$RPM_INSTALL_PREFIX\n\n"
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io start pg${MAJOR_VER//[.]/}\n\n"
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io stop pg${MAJOR_VER//[.]/}\n"
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io restart  pg${MAJOR_VER//[.]/}\n\n"
    printf "\n"
fi

%preun
if [ "\$1" -eq "0" ]
then
    for svc in ${PKG_NAME} postgresql-${MAJOR_VER//[.]/}
    do
        service \$svc status >/dev/null 2>\&1
        ret="\$?"
        if [ "\$ret" -eq "0" ]
        then
            printf "Stopping: \$svc \n"
            service \$svc stop
            if [ "\$?" -ne 0 ]
            then
                printf "Cannot stop \$svc\n"
                exit 1
            else
                if [ -f /bin/systemctl ]
                then
                    /bin/systemctl disable \$svc
                else
                    /sbin/chkconfig --del \$svc
                fi
            fi
        elif [ "\$ret" -eq 3 ]
        then
            printf "Service already stopped\n"
        fi
    done
fi

%postun
if [ "\$1" -eq "0" ]; then
  #Action is uninstallation, not called due to upgrade of a new package
  rm /etc/init.d/$INITD 2>/dev/null
  rm /usr/lib/systemd/system/$INITD.service 2>/dev/null
  rm -rf /etc/pgenv 2>/dev/null
  
  echo "Uninstallation complete."
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
$DIRS

%define date    %(echo \`LC_ALL="C" date +"%a %b %d %Y"\`)

%changelog
* %{date} PGEDGE <denis@lussier.io>
- Packaging PostgreSQL $FULL_VERSION-$RELEASE

EOF
}

function buildRPM {
 echo "Bulding RPM"
 echo "Remove /opt/ and /opt/postgres from SPECS manually and then continue"
 cat ~/$SPEC_OUTPUT | grep -v \/opt\/$ | grep -v \/opt\/postgres\/$ | grep -v \/opt\/postgres\/pgha\/$ > ~/$SPEC_OUTPUT.t
 cp ~/$SPEC_OUTPUT.t ~/$SPEC_OUTPUT
# read 
 echo "Building $ARCH rpm..."
rpmbuild -ba ~/$SPEC_OUTPUT #--sign
# expect -c "
#spawn rpmbuild -ba $HOME/$SPEC_OUTPUT 
#expect -exact \"Enter pass phrase: \" {send \"jaxc0rCam1\r\"; interact}
#"
###rpmbuild -ba --sign ~/$SPEC_OUTPUT 
# /mnt/hgfs/pgrpm/rpmbuild_expect.exp "~/$SPEC_OUTPUT"
printf "$MAJOR_VER :: $MINOR_VER :: $RELEASE\n"
mv ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/$PKG_NAME-$MAJOR_VER.$MINOR_VER-$RPM_RELEASE.x86_64.rpm ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/postgresql-$MAJOR_VER.$MINOR_VER-$RELEASE-x64-pgedge.rpm

saveDir=/build/`date +'%Y-%m-%d'`
test -d $saveDir
if [ "$?" -ne 0 ]
then
    mkdir $saveDir
fi

cp ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/postgresql-$MAJOR_VER.$MINOR_VER-$RELEASE-x64-pgedge.rpm $saveDir
printf "Saved build to: $saveDir\n"
printf "RPMBUild returned: $?\n\n\n"

if [ -f ~/.rpmmacros.oscg.bak ];
then
  echo "Restoring .rpmmacros ..."
  mv ~/.rpmmacros.oscg.bak ~/.rpmmacros 
fi

   printf "Spec Output: $SPEC_OUTPUT\n"
}


##########################################
#      Debian Functions
##########################################

function createDEBBuildStructure {
  echo "Creating deb build structure..."
  rm -rf ~/$PG_BUILD_DIR_NAME

  mkdir -p ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN

  tar -xf $PG_TRANSFORMED_TAR -C ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR
}

function createDEBControl {
FULL_VERSION="$MAJOR_VER.$MINOR_VER-$RELEASE"

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/control
Package: $PKG_NAME
Version: $FULL_VERSION
Section: database
Priority: optional
Architecture: amd64 
Maintainer: PGEDGE.com <luss@github> 
Description: PostgreSQL debian package by PGEDGE 
 PostgreSQL debian package, created and maintained by PGEDGE
Homepage: http://pgedge.com
EOF

#cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/conffiles
#/etc/init.d/$INITD
#EOF

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/preinst
#!/bin/bash

arg="\$1"
if [ "\$arg" = "upgrade" ]
then
    printf "\n\n=====  UPGRADE FAILURE ================\n"
    exit 1
fi

EOF
chmod 755 ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/preinst

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/postinst
#!/bin/bash

edg=/opt/pgedge



ln -s $edg/pg${MAJOR_VER//[.]/}/bin/psql /usr/bin/psql 2>/dev/null
ln -s $edg/pg${MAJOR_VER//[.]/}/lib/libpq.so.5 /usr/lib64/libpq.so.5 2>/dev/null

# Post installation actions
printf "\n\t======================================\n\n"
printf "\tBinaries installed at: /opt/postgresql\n\n"
printf "\t  sudo $edg start pg${MAJOR_VER//[.]/}\n\n"
printf "\t  sudo $edg stop pg${MAJOR_VER//[.]/}\n"
printf "\t  sudo $edg restart  pg${MAJOR_VER//[.]/}\n\n"
printf "\n"

EOF
chmod 755 ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/postinst

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/prerm
#!/bin/bash

arg="\$1"
if [ "\$arg" = "remove" ]
then
    for svc in ${PKG_NAME} postgresql-${MAJOR_VER//[.]/}
    do
        service \$svc status >/dev/null 2>\&1
        ret="\$?"
        if [ "\$ret" -eq "0" ]
        then
            printf "Stopping: \$svc \n"
            service \$svc stop
            if [ "\$?" -ne 0 ]
            then
                printf "Cannot stop \$svc\n"
                exit 1
            else
                if [ -f /bin/systemctl ]
                then
                    /bin/systemctl disable \$svc
                fi
            fi
        elif [ "\$ret" -eq 3 ]
        then
            printf "Service already stopped\n"
        fi
    done
fi    

EOF
chmod 755 ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/prerm

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/postrm
#!/bin/bash
printf "Removal Complete\n"
EOF
chmod 755 ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/postrm

#Create directory structure for copyright and minimal documentation
mkdir -p ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME
cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/copyright
PostgreSQL Debian Package by PGEDGE

Copyright: 
  Copyright (c) 2020. PGEDGE

License: 
  The PostgreSQL binaries are licensed under PostgreSQL License. See http://www.postgresql.org/about/licence
  The value additions in form of debian package and additional scripts by PGEDGE is licensed under GPL+
On Debian systems, the complete text of the GNU General	Public License can be found in "/usr/share/common-licenses/GPL"

EOF


cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/changelog
$PKG_NAME ($FULL_VERSION) stable; urgency=high

  * http://www.postgresql.org/about/news/1656/

EOF
cp ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/changelog ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/changelog.Debian
gzip --best ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/changelog
gzip --best ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/usr/share/doc/$PKG_NAME/changelog.Debian
}

function buildDEB() {
  OLDDIR=`pwd`
  cd ~/$PG_BUILD_DIR_NAME
  fakeroot dpkg-deb --build $DEBIAN_DIR
  #dpkg-sig --sign builder -k PGEDGE $DEBIAN_DIR.deb 
  saveDir=/build/`date +'%Y-%m-%d'`
  test -d $saveDir
  if [ "$?" -ne 0 ]
  then
      mkdir $saveDir
  fi
  cp $DEBIAN_DIR.deb $saveDir
  cd "$OLDDIR"
}

#Start
convertToPackageFriendly 
if [ -f /etc/issue ];
then
 grep -i 'ubuntu' /etc/issue &> /dev/null
 if [ $? == 0 ];
 then
    createDEBBuildStructure
    createDEBControl
    buildDEB
 else
    createRPMBuildStructure 
    createRPMSpec 
    buildRPM
 fi
else
 echo "/etc/issue not found. Please contact feedback@pgedge.org."
fi
exit 0
