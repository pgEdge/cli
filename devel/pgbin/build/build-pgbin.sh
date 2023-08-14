
# set -x

source versions.sh

archiveDir="/opt/builds/"
baseDir="`pwd`/.."
workDir=`date +%Y%m%d_%H%M`
buildLocation=""

osArch=`getconf LONG_BIT`
 
sharedLibs=/opt/pgbin-build/pgbin/shared/lib/
sharedBins=/opt/pgbin-build/pgbin/shared/bin/
includePath="$baseDir/shared/include"

pgTarLocation=""
pgSrcDir=""
pgSrcV=""
pgShortV=""
pgBldV=1
pgOPT=""

sourceTarPassed=0
archiveLocationPassed=0
buildVersionPassed=0

buildODBC=0

scriptName=`basename $0`


function printUsage {
echo "
Usage:

$scriptName [OPTIONS]

Required Options:
	-a      Target build location, the final tar.bz2 would be placed here
	-t      PostgreSQL Source tar ball.

Optional:
	-n      Build number, defaults to 1.
	-c      Copy tarFile to \$IN/postgres/pgXX
	-h      Print Usage/help.

";
}


function checkPostgres {
	
	if [[ ! -e $pgTarLocation ]]; then
		echo "File $pgTarLocation not found .... "
		printUsage
		exit 1
	fi	

	cd $baseDir	
	mkdir -p $workDir
	cd $workDir
	mkdir -p logs
	
	tarFileName=`basename $pgTarLocation`
	pgSrcDir=`tar -tf $pgTarLocation | grep HISTORY`
	pgSrcDir=`dirname $pgSrcDir`
	
	tar -xzf $pgTarLocation
		
	isPgConfigure=`$pgSrcDir/configure --version | head -1 | grep "PostgreSQL configure" | wc -l`
	
	if [[ $isPgConfigure -ne 1 ]]; then
		echo "$tarFileName is not a valid postgresql source tarball .... "
		exit 1
	else
		pgSrcV=`$pgSrcDir/configure --version | head -1 | awk '{print $3}'`
		echo "pgSrcV=$pgSrcV/rc"
		if [[ "${pgSrcV/rc}" =~ ^16beta* ]]; then
			pgShortV="16"
			bndlPrfx=pg16
			if [ "$OS" == "osx" ]; then
				pgOPT="--without-icu"
			else
				pgOPT="--with-zstd --with-lz4 --with-icu"
			fi

		elif [[ "${pgSrcV/rc}" =~ ^15.* ]]; then
			pgShortV="15"
			bndlPrfx=pg15
			if [ "$OS" == "osx" ]; then
				pgOPT="--without-icu"
			else
				pgOPT="--with-zstd --with-lz4 --with-icu"
			fi
                        
		elif [[ "${pgSrcV/rc}" =~ ^14.* ]]; then
			pgShortV="14"
			bndlPrfx=pg14
			pgOPT="--with-lz4"
		elif [[ "${pgSrcV/rc}" =~ ^13.* ]]; then
			pgShortV="13"
			bndlPrfx=pg13
			pgOPT=""
		elif [[ "${pgSrcV/rc}" =~ ^12.* ]]; then
			pgShortV="12"
			bndlPrfx=pg12
			pgOPT=""
		elif [[ "${pgSrcV/rc}" =~ ^11.* ]]; then
			pgShortV="11"
			bndlPrfx=pg11
			pgOPT=""
		else
			echo "ERROR: Could not determine Postgres Version for '$pgSrcV'"
			exit 1
		fi
		
	fi
}



function checkODBC {
    cd $baseDir
    mkdir -p $workDir

    cd $baseDir/$workDir

    odbcSourceDir=`dirname $(tar -tf $odbcSourceTar | grep "odbcapi.c")`

    tar -xzf $odbcSourceTar

    return 0
}


function buildPostgres {
	echo "# buildPOSTGRES"	
	cd $baseDir/$workDir/$pgSrcDir

	if [ "$pgShortV" == "15" ] || [ "$pgShortV" == "16" ]; then
		if [ "$DIFF1" == "" ]; then
			echo "std postgres build, no patches to apply"
		elif [ ! -f "$DIFF1" ]; then
			echo "# DIFF1 not found : $DIFF1"
			exit 1
		else
			echo "# Applying $DIFF1"
			patch -p1 -i $DIFF1
			rc=$?
			if [ "$rc" == "0" ]; then
				echo "# patch succesfully applied"
			else
				echo "# FATAL ERROR: applying patch"
				exit 1
			fi
		fi
	fi

	mkdir -p $baseDir/$workDir/logs
	#buildLocation="$baseDir/$workDir/build/pg$pgShortV-$pgSrcV-$pgBldV-$OS"
	buildLocation="$baseDir/$workDir/build/$bndlPrfx-$pgSrcV-$pgBldV-$OS"
	echo "# buildLocation = $buildLocation"
	arch=`arch`

	conf="--disable-rpath $pgOPT"
	echo "OS=$OS"
	if [ $OS == "osx" ] || [ $OS == "el8" ]; then
		conf="$conf --without-python --without-perl"
	else
		conf="$conf  --with-libxslt --with-libxml"
		conf="$conf --with-uuid=ossp --with-gssapi --with-ldap --with-pam --enable-debug --enable-dtrace"
		conf="$conf --with-llvm LLVM_CONFIG=/usr/bin/llvm-config-64 --with-openssl --with-systemd --enable-tap-tests"
		conf="$conf --with-python PYTHON=/usr/bin/python3.9"
	fi

	gcc --version
	echo "#  @`date`  $conf"
	configCmnd="./configure --prefix=$buildLocation $conf" 

	export LD_LIBRARY_PATH=$sharedLibs
	export LDFLAGS="$LDFLAGS -Wl,-rpath,'$sharedLibs' -L$sharedLibs"
	export CPPFLAGS="$CPPFLAGS -I$includePath"

	log=$baseDir/$workDir/logs/configure.log
	$configCmnd > $log 2>&1
	if [[ $? -ne 0 ]]; then
		echo "# configure failed, cat $log"
		exit 1
	fi

	echo "#  @`date`  make -j $CORES" 
	log=$baseDir/$workDir/logs/make.log
	make -j $CORES > $log 2>&1
	if [[ $? -ne 0 ]]; then
		echo "# make failed, check $log"
		exit 1
	fi

	echo "#  @`date`  make install"
	log=$baseDir/$workDir/logs/make_install.log
	make install > $log 2>&1
	if [[ $? -ne 0 ]]; then
		echo "# make install failed, cat $log"
		exit 1
 	fi

	cd $baseDir/$workDir/$pgSrcDir/contrib
	echo "#  @`date`  make -j $CORES contrib"
	make -j $CORES > $baseDir/$workDir/logs/contrib_make.log 2>&1
	if [[ $? -eq 0 ]]; then
		echo "#  @`date`  make install contrib"
		make install > $baseDir/$workDir/logs/contrib_install.log 2>&1
		if [[ $? -ne 0 ]]; then
			echo "Failed to install contrib modules ...."
		fi
	fi

	oldPath=$PATH
	PATH="$PATH:$buildLocation/bin"

	echo "# skipping make docs"
	return

	cd $baseDir/$workDir/$pgSrcDir/doc
	echo "#  @`date`  make docs"
	make > $baseDir/$workDir/logs/docs_make.log 2>&1
	if [[ $? -eq 0 ]]; then
		make install > $baseDir/$workDir/logs/docs_install.log 2>&1
		if [[ $? -ne 0 ]]; then
			echo "Failed to install docs .... "
		fi
	else
		echo "Make failed for docs ...."
		return 1
	fi
}


function buildODBC {
        echo "# buildODBC()"
        cd $baseDir/$workDir/$odbcSourceDir

	export LD_LIBRARY_PATH=$sharedLibs:$buildLocation/lib
        export OLD_PATH=`echo $PATH`
        export PATH=$sharedBins:$PATH
       
	echo "#   configure     @ `date`" 
	log="$baseDir/$workDir/logs/odbc_configure.log"
        ./configure --prefix=$buildLocation --with-libpq=$buildLocation LDFLAGS="-Wl,-rpath,$sharedLibs -L$sharedLibs" CFLAGS=-I$includePath > $log 2>&1
        if [[ $? -ne 0 ]]; then
                echo "FATAL ERROR: check $log"
		unset LD_LIBRARY_PATH
                return 1
        fi

	echo "#  @date  make -j $CORES"
        log="$baseDir/$workDir/logs/odbc_make.log"
        make -j $CORES > $log 2>&1
        if [[ $? -ne 0 ]]; then
                echo "FATAL ERROR: check $log"
		unset LD_LIBRARY_PATH
                export PATH=$OLD_PATH
                return 1
        fi

	echo "#  @`date`   make install"
        make install > $baseDir/$workDir/logs/odbc_install.log 2>&1
        if [[ $? -ne 0 ]]; then
                echo "Failed to install ODBC Driver ...."
		unset LD_LIBRARY_PATH
                export PATH=$OLD_PATH
                return 1
        fi
	
	unset LD_LIBRARY_PATH
        export PATH=$OLD_PATH
	return 0
}


function copySharedLibs {
	##set -x
	echo "#"
	echo "# copySharedLibs()"
	cp -Pp $sharedLibs/* $buildLocation/lib/
	return
}

function updateSharedLibPathsForLinux {
  libPathLog=$baseDir/$workDir/logs/libPath.log
  echo "#   updateSharedLibPathsForLinux()"

  cd $buildLocation/bin
  echo "#     looping thru executables"
  for file in `ls -d *` ; do
	##echo "### $file"
	chrpath -r "\${ORIGIN}/../lib" "$file" >> $libPathLog 2>&1
  done

  libSuffix="*so*"

  cd $buildLocation/lib
  echo "#     looping thru shared objects"
  for file in `ls -d $libSuffix 2>/dev/null` ; do
	##echo "### $file"
	chrpath -r "\${ORIGIN}/../lib" "$file" >> $libPathLog 2>&1
  done

  echo "#     looping thru lib/postgresql "
  if [[ -d "$buildLocation/lib/postgresql" ]]; then
	cd $buildLocation/lib/postgresql
	##echo "### $file"
    for file in `ls -d $libSuffix 2>/dev/null` ; do
      chrpath -r "\${ORIGIN}/../../lib" "$file" >> $libPathLog 2>&1
    done
  fi

}

function fixMacOSBinary {
  binary="$1"
  libPathPrefix="$2"
  rpath="$3"
  libPathLog="$4"

  otool -L "$binary" |
	awk '/^[[:space:]]+'"$libPathPrefix"'/ {print $1}' |
	while read lib; do
	  install_name_tool -change "$lib" '@rpath/'$(basename "$lib") "$binary" >> $libPathLog 2>&1
	done

  if otool -l "$binary" | grep -A3 RPATH | grep -q "$sharedLibs"; then
	install_name_tool -rpath "$sharedLibs" "$rpath" "$binary" >> $libPathLog 2>&1
  fi
}

function updateSharedLibPathsForMacOS {
  libPathLog=$baseDir/$workDir/logs/libPath.log
  escapedBaseDir="$(echo "$baseDir" | sed 's@/@\\/@g')"
  echo "#   updateSharedLibPathsForMacOS()"

  cd $buildLocation/bin
  echo "#     looping thru executables"
  for file in `ls -d *` ; do
	##echo "### $file"
	fixMacOSBinary "$file" "$escapedBaseDir" '@executable_path/../lib' "$libPathLog"
  done

  libSuffix="*.dylib*"
  cd $buildLocation/lib
  echo "#     looping thru shared objects"
  for file in `ls -d $libSuffix 2>/dev/null` ; do
	##echo "### $file"
	fixMacOSBinary "$file" "$escapedBaseDir" '@loader_path/../lib' "$libPathLog"
  done

  libSuffix="*.so*"
  echo "#     looping thru lib/postgresql"
  if [[ -d "$buildLocation/lib/postgresql" ]]; then
	cd $buildLocation/lib/postgresql
	##echo "### $file"
    for file in `ls -d $libSuffix 2>/dev/null` ; do
	  fixMacOSBinary "$file" "$escapedBaseDir" '@loader_path/../../lib' "$libPathLog"
    done
  fi

}


function updateSharedLibPaths {
	echo "#"
	echo "# updateSharedLibPaths()"

	if [ `uname` == "Linux" ]; then
		updateSharedLibPathsForLinux
	else
		updateSharedLibPathsForMacOS
	fi
}

function createBundle {
	echo "#"
	echo "# createBundle()"

	cd $baseDir/$workDir/build

	##Tar="pg$pgShortV-$pgSrcV-$pgBldV-$OS"
	Tar="$bndlPrfx-$pgSrcV-$pgBldV-$OS"

	##Cmd="tar -cjf $Tar.tar.bz2 $Tar pg$pgShortV-$pgSrcV-$pgBldV-$OS" 
	Cmd="tar -cjf $Tar.tar.bz2 $Tar $bndlPrfx-$pgSrcV-$pgBldV-$OS" 

	tar_log=$baseDir/$workDir/logs/tar.log
        $Cmd >> $tar_log 2>&1
	if [[ $? -ne 0 ]]; then
		echo "Unable to create tar for $buildLocation, check logs .... "
		echo "tar_log=$tar_log"
		cat $tar_log
		return 1
	else
		mkdir -p $archiveDir/$workDir
		mv "$Tar.tar.bz2" $archiveDir/$workDir/

		cd /opt/pgcomponent
		pgCompDir="pg$pgShortV"
        	rm -rf $pgCompDir
		mkdir $pgCompDir 
		tar -xf "$archiveDir/$workDir/$Tar.tar.bz2" --strip-components=1 -C $pgCompDir
	fi
	tarFile="$archiveDir/$workDir/$Tar.tar.bz2"
	if [ "$optional" == "-c" ]; then
		##cmd="cp -p $tarFile $IN/postgres/pg$pgShortV/."
		cmd="cp -p $tarFile $IN/postgres/$bndlPrfx/."
		echo $cmd
		$cmd
	else
		echo "#    tarFile=$tarFile"
	fi
	return 0
}

function checkCmd {
	$1
	rc=$?
	if [ "$rc" == "0" ]; then
		return 0
	else
		echo "FATAL ERROR in $1"
		echo ""
		exit 1
	fi
}


function buildApp {
	checkFunc=$1
	buildFunc=$2

	echo "#"	
	$checkFunc
	if [[ $? -eq 0 ]]; then
		$buildFunc
		if [[ $? -ne 0 ]]; then
			echo "FATAL ERROR: in $buildFunc ()"
			exit 1
		fi
	else
		echo "FATAL ERROR: in $checkFunc ()"
		exit 1
	fi
}


function isPassed { 
	if [ "$1" == "0" ]; then
		echo "FATAL ERROR: $2 is required"
		printUsage
		exit 1
	fi
}

###########################################################
#                  MAINLINE                               #
###########################################################

if [[ $# -lt 1 ]]; then
	printUsage
	exit 1
fi

echo "### $scriptName ###"

optional=""
while getopts "t:a:o:n:hc" opt; do
	case $opt in
		t)
			if [[ $OPTARG = -* ]]; then
       				((OPTIND--))
				continue
      			fi
			pgTarLocation=$OPTARG
			sourceTarPassed=1
			echo "# -t $pgTarLocation"
		;;
		a)
			if [[ $OPTARG = -* ]]; then
				((OPTIND--))
			fi
			archiveDir=$OPTARG
			archiveLocationPassed=1
			echo "# -a $archiveDir"
		;;
		o) 	if [[ OPTARG = -* ]]; then
				((OPTIND--))
				continue
			fi
			buildODBC=1
			odbcSourceTar=$OPTARG
			echo "# -o $odbcSourceTar"
		;;
		n)	
			pgBldV=$OPTARG
			echo "# -n $pgBldV"
		;;
		c)
			optional="-c"
		;;
		h)
			printUsage
			exit 0
		;;
		esac
done
if [ ! "$optional" == "" ]; then
	echo "# $optional"
fi
echo "###"

isPassed "$archiveLocationPassed" "Target build location (-a)"
isPassed "$sourceTarPassed" "Postgres source tarball (-t)"

checkCmd "checkPostgres"
checkCmd "buildPostgres"

if [ "$buildODBC" == "1" ]; then
  buildApp "checkODBC" "buildODBC"
fi

copySharedLibs
checkCmd "updateSharedLibPaths"
checkCmd "createBundle"
rc=$?
echo "# rc=$rc"
echo "#"

exit 0
