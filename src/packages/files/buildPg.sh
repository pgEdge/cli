#!/bin/bash

# buildPg.sh

installRoot=$HOME/software/pg
buildRoot=$installRoot/build
pgFilePrefix="postgresql-"
pgFilePostfix=".tar.bz2"
buildSave="/tmp/build"

while [ -n "$1" ]
do
    case "$1" in
    --versions) 
            shift
            versions="$1"
            shift
        ;;
    --platform)
            shift
            platform="$1"
            shift
        ;;
    --rel)
            shift
            rel="$1"
            shift
        ;;
    --arch) 
            shift
            arch="$1"
            shift
        ;;
    * )
        printf "You must specify the versions to build and platform name\n"
        printf "\t$0 --versions '9.1.23 9.4.8' --platform el7 --rel <relnum>\n"
        exit 1
        ;;
    esac
done

if [ -z "$platform" -o -z "$rel" -o -z "$versions" -o -z "$arch" ]
then
    printf "You must specify the versions to build and platform name\n"
    printf "\t$0 --versions '9.1.23 9.4.8' --platform el7 --rel <relnum>\n"
    exit 1
fi


if [ -d "$buildSave" ]
then
    rm -rf $buildSave
fi

mkdir -p $buildSave

test -d $buildRoot
if [ "$?" -ne 0 ] 
then
    mkdir -p $buildRoot
fi

test -d $installRoot
if [ "$?" -ne 0 ] 
then
    mkdir -p $installRoot
fi

pushd $buildRoot

echo "$versions" | grep -q 'latest'

if [ "$?" -eq 0 ]
then
    
    majors=`echo $versions | awk '{for(i=2;i<=NF;++i)printf("%s ",$i)}'`

    printf "Okay, I found: $majors ::: from $versions\n"

    versions=""

    if [ -z "$majors" ]
    then
      printf "I don't trust majors\n"
      majors='9.5 9.6'
    elif [ "$majors" == "all" ]
    then
      majors="9.2 9.3 9.4 9.5 9.6"
    fi

    printf "Computing versions... "
    for ver in $majors
    do
        versions="$versions "`curl -l ftp://ftp.postgresql.org/pub/source/ 2>/dev/null | grep ^v$ver | sed 's/v//g'| sort -t '.' -n -k3 -r | head -n 1`
    done
    
    versions=`echo $versions | sed 's/^ //g'`
    
    printf "Based on computation, we will build:\n"
    printf "\t$versions\n\n\n\n"
    
fi

for version in $versions
do
    majornodot=`echo $version | awk -F'[a-b]' '{print $1}' | awk -F'.' '{print $1$2}'`
    vnodot=`echo $version | sed 's/\.//g' | sed 's/[a-zA-Z]*//g'`
    printf "Preparing for $version\n"
    dirname=$pgFilePrefix"$version"
    tarball=$dirname$pgFilePostfix
    
    # Don't re-download the tarball
    test -f $tarball
    
    if [ "$?" -ne 0 ] 
    then
        curl -O https://ftp.postgresql.org/pub/source/v$version/$tarball
    fi
    
    # Don't extract if the dir already exists
    test -d $dirname

    if [ "$?" -ne 0 ] 
    then
        tar -xvf $tarball
    fi
    
    pushd $dirname
   
    test -f "config.log"
    
    if [ "$?" -ne 0 ] 
    then
        make distclean
    fi

    sharedLibs="$installRoot/$version/lib"
    
    ./configure --prefix=$installRoot/$version --with-openssl --with-ldap \
                                               --with-perl \
                                               --with-python --with-libxslt \
                                               --with-libxml --with-uuid=ossp \
                                               --with-gssapi --with-kerberos \
                                               --with-tcl --with-includes=$INCLUDES

    if [ "$?" -ne 0 ] 
    then
        exit 1
    fi
    
    # Build
    make -j6

    if [ "$?" -ne 0 ] 
    then
        exit 1
    fi

    # Test
    make check

    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

    # Install
    make install

    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

    pushd contrib

    make -j 6

    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

    make install

    if [ "$?" -ne 0 ]
    then
        exit 1
    fi

    popd

    pushd $installRoot/$version

    # Fix shlib paths
    pushd bin
    for file in * 
    do
        chrpath -r "\${ORIGIN}/../lib/" $file
    done
    popd
#    pushd lib
#    for file in *so*
#    do
#        chrpath -r "\${ORIGIN}/../lib/" $file
#    done
#    popd
#    pushd lib/postgresql
#    for file in *.so
#    do
#        chrpath -r "\${ORIGIN}/../../lib/" $file
#    done
#    popd 

    printf "Saving artifacts at: $installRoot/$version"

    rpmPrep="pg$majornodot-$version-$rel-linux64" 
    
    tar -cjvf $buildSave/$rpmPrep.tar.bz2 bin include lib share

    popd
     
    pushd $installRoot/$version
    # Prep for bigsql packaging
    dirName="pg$majornodot-$version-$rel-$platform-$arch" 
    tarName="$dirName.tar.bz2" 

    mkdir -p "$installRoot/$dirName"

    cp -Rp bin include lib share "$installRoot/$dirName"

    popd

    pushd "$installRoot/$dirName/../" 

    tar -cjvf $tarName "$dirName"

    cp $tarName $buildSave/

    popd


#    while [ "$vnodot" -lt 1024 ]
#    do
#        vnodot=$(($vnodot * 10))
#    done
    
    #Build an ENV file
#    cat <<_EOF_ > $installRoot/$version/this.env
#export PGHOME=$installRoot/$version
#export PATH=\$PGHOME/bin:\$PATH
#export PGDATA=$installRoot/$version/data
#export PGPORT=$vnodot
#export PGUSER=postgres
#export LD_LIBRARY_PATH=\$PGHOME/lib
#export PGDATABASE=postgres
#_EOF_
#
#    chmod 0755 $installRoot/$version/this.env
#    
#    source $installRoot/$version/this.env
#    
#    initdb -U postgres
    
    popd
    
done
    
