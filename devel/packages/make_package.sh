#! /bin/bash

#This script generates an RPM or DEB package.

#Input: Directory containing appropriate pg binaries tar.gz.
#Output: RPM in ~/pg_pgsqlio_build/RPMS/i386 or x86_64
#        DEB in ~/pg_pgsqlio_build

HELP_TEXT() {
    printf "\n"
    printf "  Required Flags:\n"
    printf "      --major_version <9.6>\n"
    printf "          Specify a PostgreSQL Major Version Number\n"
    printf "      --minor_version <1>\n"
    printf "          Specify a PostgreSQL Minor Version Number\n"
    printf "      --release <1>\n"
    printf "          Specify an internal Release Number\n"
    printf "      --rpm_release <1>\n"
    printf "          Specify an RPM Build Release Number\n"
    printf "\n"
    printf "  Optional Flags:\n"
    printf "      --pkg_name postgres   DEFAULT=postgres\n"
    printf "          Specify a filename prefix for the final RPM package produced\n"
    printf "      --source_dir </tmp>   DEFAULT=/tmp\n"
    printf "          Specify the source directory in which sandbox can be found,\n"
    printf "           otherwise we will attempt to download it to this specified directory\n"
    printf "      --mirror_url http://localhost   DEFAULT=http://loclahost:8000\n"
    printf "          Specify the source URL in which a sandbox can be found\n"

    # Deprecated here, Functionality moved to io
    #printf "      --initscript </opt/startup_scripts/sys-V-init>\n"
    #printf "          (Specify a source directory containing the PostgreSQL sys V init script)\n"
    #printf "      --systemd_scripts </opt/startup_scripts/systemd_init>\n"
    #printf "          (Specify a source directory containing the PostgreSQL systemd init script)\n"
    printf "\n"
}
# Default options
MIRROR_URL="http://localhost:8000"
SOURCE_DIR="/tmp"
PKG_NAME="postgresql"
while [ -n "$1" ] 
do
    case "$1" in
    --major_version | -majorver ) 
            shift
            MAJOR_VERSION="$1"
            shift
            ;;
    --minor_version | -minorver )
            shift
            MINOR_VERSION="$1"
            shift
            ;;
    --release | -r ) 
            shift
            RELEASE="$1"
            shift
            ;;
    --rpm_release ) 
            shift
            RPM_RELEASE="$1"
            shift
            ;;
    --pkg_name ) 
            shift
            PKG_NAME="$1"
            shift
            ;;
    --sourcedir | --source_dir ) 
            shift
            SOURCE_DIR="$1"
            shift
            ;;
    --mirror_url ) 
            shift
            MIRROR_URL="$1"
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

#VARS_STRING="$MAJOR_VERSION $MINOR_VERSION $RELEASE $RPM_RELEASE $PKG_NAME $SOURCE_DIR $INIT_SCRIPT_SRC $SYSTEMD_SCRIPTS "

#VAR_NUM="$VARS_STRING | wc -w"

if [ -z "$MAJOR_VERSION" ] ;then
    printf "\n"
    printf "ERROR: Must set --major_version\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi
if [ -z "$MINOR_VERSION" ] ;then
    printf "\n"
    printf "ERROR: Must set --minor_version\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi
if [ -z "$RELEASE" ] ;then
    printf "\n"
    printf "ERROR: Must set --release\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi
if [ -z "$RPM_RELEASE" ] ;then
    printf "\n"
    printf "ERROR: Must set --rpm_release\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi
if [ -z "$PKG_NAME" ] ;then
    printf "\n"
    printf "ERROR: Must set --pkg_name\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi
if [ -z "$SOURCE_DIR" ] ;then
    printf "\n"
    printf "ERROR: Must set --source_dir\n"
    printf "\n"
    printf "    Please read below for details.\n"
    printf "\n"
    HELP_TEXT
    exit 1
fi

PKG_NAME="$PKG_NAME${MAJOR_VERSION//[.]/}"
PG_NAME="postgresql${MAJOR_VERSION//[.]/}"
SANDBOX_NAME="pgsql-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-linux64.tar.bz2"

echo --------------------
echo Locating Source File
echo --------------------
echo

if [ ! -f $SOURCE_DIR/$SANDBOX_NAME ]
then
    echo "***Input file not found, attempting to download from Mirror***"

    echo ----------------------------------------------------
    echo Downloading Sandbox $SANDBOX_NAME
    echo ----------------------------------------------------

    echo 
    echo        Download URL is:        
    echo 
    echo $MIRROR_URL$SANDBOX_NAME

    curl -o $SOURCE_DIR/$SANDBOX_NAME $MIRROR_URL$SANDBOX_NAME
else
    serverSha=`curl $MIRROR_URL$SANDBOX_NAME.sha512 2>/dev/null | awk '{print $1}'`
    localSha=`sha512sum $SOURCE_DIR/$SANDBOX_NAME | awk '{print $1}'`
    if [ "$serverSha" = "$localSha" ]
    then
        echo "***Source file $SOURCE_DIR/$SANDBOX_NAME found.  It will be assimilated into the collective.***"
    else
        printf "New Version of $SOURCE_DIR/$SANDBOX_NAME found on server, downloading\n\n"
        rm -f $SOURCE_DIR/$SANDBOX_NAME
        curl -o $SOURCE_DIR/$SANDBOX_NAME $MIRROR_URL$SANDBOX_NAME
    fi
fi
echo ------------------------------------
echo PostgreSQL RPM/DEB generation script
echo ------------------------------------

#if [ $# -lt 1 -o $# -gt 2 ];
#then
#    echo "Usage: $0 <source dir> [<dest dir>]"
#    exit 127
#fi

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

#INSTALLATION_PATH="/opt/postgresql/pg`echo $MAJOR_VERSION | sed 's/\.//g'`"
INSTALLATION_PATH="/opt/postgresql"
PGINSTALLATION_PATH="$INSTALLATION_PATH/pg`echo $MAJOR_VERSION | sed 's/\.//g'`"
PG_LINUX_TAR="$SOURCE_DIR/bigsql-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-linux64.tar.bz2"
TMP_PREFIX="/tmp/PG_PGSQLIO_BUILD"
TMP_ROOT="$TMP_PREFIX$INSTALLATION_PATH"
TMP_INITD="$TMP_ROOT/pg`echo $MAJOR_VERSION | sed 's/\.//g'`/startup"
INITD="postgresql-`echo $MAJOR_VERSION | sed 's/\.//g'`"
PG_BUILD_DIR_NAME="pg_pgsqlio_build"
PG_TRANSFORMED_TAR="/tmp/$PKG_NAME-$MAJOR_VERSION.$MINOR_VERSION-$RPM_RELEASE-$OS_PLATFORM-bigsql.tar.gz"
ENVFILE_NAME="pg${MAJOR_VERSION//[.]/}.env"
ENVFILE="$TMP_ROOT/$ENVFILE_NAME"
DEBIAN_DIR="postgresql-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-$DEBIAN_ARCH-bigsql"
RPMOSUSER="postgres"
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
	 mv $TMP_ROOT/pg${MAJOR_VERSION//[.]/}-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-linux64/* $TMP_ROOT
	 rm -r $TMP_ROOT/pg${MAJOR_VERSION//[.]/}-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-linux64
	 #rm -rf $TMP_ROOT/stackbuilder
	 #rm -rf $TMP_ROOT/pgAdmin3
	 rm -f $PG_TRANSFORMED_TAR
#	 touch $ENVFILE 
	 #Dump default environment values
#	 cat <<ENVEOF > $ENVFILE 
##!/bin/bash
#export PGHOME=$INSTALLATION_PATH/pg${MAJOR_VERSION//[.]/}
#export PGDATA=$INSTALLATION_PATH/data/pg${MAJOR_VERSION//[.]/}
#export PATH=$INSTALLATION_PATH/pg${MAJOR_VERSION//[.]/}/bin:\$PATH
#export LD_LIBRARY_PATH=$INSTALLATION_PATH/pg${MAJOR_VESION//[.]/}/lib:\$LD_LIBRARY_PATH
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
%_gpg_name PGSQL-IO
EOF
}
function createRPMSpec {
  echo "Preparing rpm sources..."
  if [ -f $PG_TRANSFORMED_TAR ];
  then
	 cp $PG_TRANSFORMED_TAR ~/$PG_BUILD_DIR_NAME/SOURCES/
  fi

  echo "Creating spec file..."
  SPEC_OUTPUT="$PG_BUILD_DIR_NAME/SPECS/$PKG_NAME-$MAJOR_VERSION.$MINOR_VERSION-$OS_PLATFORM-bigsql.spec"

  FILES=$(/bin/tar -tzf $PG_TRANSFORMED_TAR | /bin/grep -v '^.*/$' | sed 's/^/\//')
  DIRS=$(/bin/tar -tvzf $PG_TRANSFORMED_TAR | grep "^d" | awk '{ print $6 }' | sed 's/^/\//' | sort | uniq)
#echo $DIRS
  FULL_VERSION="$MAJOR_VERSION.$MINOR_VERSION"
/bin/cat > ~/$SPEC_OUTPUT << EOF
%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress
%define        __prelink_undo_cmd ${nil}

Name: $PKG_NAME
Version: $FULL_VERSION
Release: $RPM_RELEASE
Vendor: PGSQL.IO
Summary: PostgreSQL RPM by PGSQL.IO
License: GPL+
Group: Applications/Databases
Source0: %{name}-%{version}-%{release}-$OS_PLATFORM-pgsqlio.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: $ARCH
URL: http://pgsql.io
Prefix: $INSTALLATION_PATH
%description
PostgreSQL by PGSQL.IO

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
ln -s \$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}/bin/psql /usr/bin/psql 2>/dev/null
ln -s \$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}/lib/libpq.so.5 /usr/lib64/libpq.so.5 2>/dev/null

cat <<ENVEOF > \$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}.env
#!/bin/bash
export PGHOME=\$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}
export PGDATA=\$RPM_INSTALL_PREFIX/data/pg${MAJOR_VERSION//[.]/}
export PATH=\$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}/bin:\$PATH
export LD_LIBRARY_PATH=\$RPM_INSTALL_PREFIX/pg${MAJOR_VESION//[.]/}/lib:\$LD_LIBRARY_PATH
export PGUSER=postgres
export PGDATABASE=postgres
ENVEOF

chmod 0755 \$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}.env

printMessage=1
# 2 means we're performing an upgrade
if [ "\$1" = "2" ]
then
    # If the env file exists, we're doing an upgrade of an initialized system
    if [ -f \$RPM_INSTALL_PREFIX/pg${MAJOR_VERSION//[.]/}.env ]
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
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io start pg${MAJOR_VERSION//[.]/}\n\n"
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io stop pg${MAJOR_VERSION//[.]/}\n"
    printf "\t  sudo \$RPM_INSTALL_PREFIX/io restart  pg${MAJOR_VERSION//[.]/}\n\n"
    printf "\n"
fi

%preun
if [ "\$1" -eq "0" ]
then
    for svc in ${PKG_NAME} postgresql-${MAJOR_VERSION//[.]/}
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
* %{date} PGSQL.IO <denis@lussier.io>
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
printf "$MAJOR_VERSION :: $MINOR_VERSION :: $RELEASE\n"
mv ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/$PKG_NAME-$MAJOR_VERSION.$MINOR_VERSION-$RPM_RELEASE.x86_64.rpm ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/postgresql-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-x64-bigsql.rpm

saveDir=/build/`date +'%Y-%m-%d'`
test -d $saveDir
if [ "$?" -ne 0 ]
then
    mkdir $saveDir
fi

cp ~/$PG_BUILD_DIR_NAME/RPMS/$ARCH/postgresql-$MAJOR_VERSION.$MINOR_VERSION-$RELEASE-x64-bigsql.rpm $saveDir
printf "Saved build to: $saveDir\n"
printf "RPMBUild returned: $?\n\n\n"

if [ -f ~/.rpmmacros.oscg.bak ];
then
  echo "Restoring .rpmmacros ..."
  mv ~/.rpmmacros.oscg.bak ~/.rpmmacros 
#else
#  rm ~/.rpmmacros
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
FULL_VERSION="$MAJOR_VERSION.$MINOR_VERSION-$RELEASE"

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/control
Package: $PKG_NAME
Version: $FULL_VERSION
Section: database
Priority: optional
Architecture: amd64 
Maintainer: PGSQL.io <denis@lussier.io> 
Description: PostgreSQL debian package by PGSQL.IO 
 PostgreSQL debian package, created and maintained by PGSQL.IO
Homepage: http://pgsql.io
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

ln -s /opt/postgresql/pg${MAJOR_VERSION//[.]/}/bin/psql /usr/bin/psql 2>/dev/null
ln -s /opt/postgresql/pg${MAJOR_VERSION//[.]/}/lib/libpq.so.5 /usr/lib64/libpq.so.5 2>/dev/null

# Post installation actions
printf "\n\t======================================\n\n"
printf "\tBinaries installed at: /opt/postgresql\n\n"
printf "\t  sudo /opt/postgresql/io start pg${MAJOR_VERSION//[.]/}\n\n"
printf "\t  sudo /opt/postgresql/io stop pg${MAJOR_VERSION//[.]/}\n"
printf "\t  sudo /opt/postgresql/io restart  pg${MAJOR_VERSION//[.]/}\n\n"
printf "\n"

EOF
chmod 755 ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/postinst

cat <<EOF > ~/$PG_BUILD_DIR_NAME/$DEBIAN_DIR/DEBIAN/prerm
#!/bin/bash

arg="\$1"
if [ "\$arg" = "remove" ]
then
    for svc in ${PKG_NAME} postgresql-${MAJOR_VERSION//[.]/}
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
PostgreSQL Debian Package by PGSQL.IO

Copyright: 
  Copyright (c) 2020. PGSQL.IO

License: 
  The PostgreSQL binaries are licensed under PostgreSQL License. See http://www.postgresql.org/about/licence
  The value additions in form of debian package and additional scripts by PGSQL.IO is licensed under GPL+
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
  #dpkg-sig --sign builder -k PGSQL-IO $DEBIAN_DIR.deb 
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
 echo "/etc/issue not found. Please contact feedback@bigsql.org."
fi
exit 0
