#!/bin/bash

##set -x

source ./versions.sh
buildOS=$OS
buildNumber=1

baseDir="`pwd`/.."
workDir="comp`date +%Y%m%d_%H%M`"
PGHOME=""

componentShortVersion=""
componentFullVersion=""
buildNumber=0

targetDir="/opt/pgbin-build/build"
sharedLibs="/opt/pgbin-build/pgbin/shared"

# Get PG Version from the provided pgBin directory
function getPGVersion {
	if [[ ! -f "$pgBin/bin/pg_config" ]]; then
		echo "pg_config is required for building components"
		echo "No such file or firectory : $pgBin/bin/pg_config "
		return 1
	fi
	pgFullVersion=`$pgBin/bin/pg_config --version | awk '{print $2}'`

        if [[ "${pgFullVersion/rc}" =~ 17d* ]]; then
                pgShortVersion="17"
        elif [[ "${pgFullVersion/rc}" =~ 16.* ]]; then
                pgShortVersion="16"
        elif [[ "${pgFullVersion/rc}" =~ 15.* ]]; then
                pgShortVersion="15"
        elif [[ "${pgFullVersion/rc}" =~ 14.* ]]; then
                pgShortVersion="14"
        elif [[ "${pgFullVersion/rc}" =~ 13.* ]]; then
                pgShortVersion="13"
        elif [[ "${pgFullVersion/rc}" =~ 12.* ]]; then
                pgShortVersion="12"
	elif [[ "${pgFullVersion/rc}" == "$pgFullVersion" ]]; then
		pgShortVersion="`echo $pgFullVersion | awk -F '.' '{print $1$2}'`"
        else
                pgShortVersion="`echo $pgFullVersion | awk -F '.' '{print $1$2}'`"
                pgShortVersion="`echo ${pgShortVersion:0:2}`"
        fi
}


function prepComponentBuildDir {
	buildLocation=$1
	rm -rf $buildLocation
	mkdir -p $buildLocation
	mkdir -p $buildLocation/bin
        mkdir -p $buildLocation/share
	mkdir -p $buildLocation/lib/postgresql/pgxs
	cp $PGHOME/bin/pg_config $buildLocation/bin/
	cp $PGHOME/bin/postgres  $buildLocation/bin/
	cp -r $PGHOME/include $buildLocation/
	cp -r $PGHOME/lib/postgresql/pgxs/* $buildLocation/lib/postgresql/pgxs/
	cp $PGHOME/lib/libpq* $buildLocation/lib/
	cp $PGHOME/lib/libssl*.so* $buildLocation/lib/
	cp $PGHOME/lib/libpgport.a $buildLocation/lib/
	cp $PGHOME/lib/libpgcommon.a $buildLocation/lib/
	#cp $PGHOME/lib/libcrypt*.so* $buildLocation/lib/
        cp $PGHOME/lib/postgresql/plpgsql.so $buildLocation/lib/postgresql/
}


function cleanUpComponentDir {
	cd $1
	rm -rf bin/pg_config
	rm -rf bin/postgres
	rm -rf lib/postgresql/plpgsql.so
	rm -rf include
	rm -rf lib/postgresql/pgxs
	rm -rf lib/libpgport.a
	rm -rf lib/libpgcommon.a
	rm -rf lib/libssl*
	rm -rf lib/libpq*
	rm -rf lib/libcrypt*

	if [[ ! "$(ls -A bin)" ]]; then
		rm -rf bin
	fi

	##if [ "$copyBin" == "false" ]; then
	##	ls -lR
	##fi
}


function  packageComponent {
	bundle="$targetDir/$workDir/$componentBundle.tgz"
	echo "$bundle"

	cd "$baseDir/$workDir/build/"
	tar -czf "$componentBundle.tgz" $componentBundle
	rm -rf "$targetDir/$workDir"
	mkdir -p "$targetDir/$workDir"
	mv "$componentBundle.tgz" "$targetDir/$workDir/"

	if [ "$copyBin" == "true" ]; then
		cp -pv $bundle $IN/postgres/$compDir/.
	elif [ "$noTar" == "true" ]; then
		echo "NO TAR"
		cd $targetDir/$workDir/
		tar -xf $componentBundle.tgz
		echo "cd $targetDir/$workDir/$componentBundle/lib/postgresql"
	fi

}

function fixMacOSBinary {
  binary="$1"
  libPathPrefix="$2"
  rpath="$3"
  libPathLog="$4"
  sharedLibsPath="$sharedLibs/lib/"

  otool -L "$binary" |
	awk '/^[[:space:]]+'"$libPathPrefix"'/ {print $1}' |
	while read lib; do
	  install_name_tool -change "$lib" '@rpath/'$(basename "$lib") "$binary" >> "$libPathLog" 2>&1
	done

  if otool -l "$binary" | grep -A3 RPATH | grep -q "$sharedLibs"; then
	install_name_tool -rpath "$sharedLibsPath" "$rpath" "$binary" >> "$libPathLog" 2>&1
  fi
}

function updateSharedLibs {
        comp=$1

        if [ `uname` == "Darwin" ]; then
          suffix="*dylib*"
        else
          suffix="*so*"
        fi

        libPathLog=$baseDir/$workDir/logs/libPath.log
        escapedBaseDir="$(echo "$baseDir" | sed 's@/@\\/@g')"

        if [[ -d $buildLocation/bin ]]; then
          cd $buildLocation/bin
          for file in `ls -d *` ; do
            if [ `uname` == "Darwin" ]; then
              fixMacOSBinary "$file" "$escapedBaseDir" '@executable_path/../lib' "$libPathLog"
            else
              chrpath -r "\${ORIGIN}/../lib" "$file" >> $libPathLog 2>&1
            fi
      	  done
        fi

        cd $buildLocation/lib
        for file in `ls -d $suffix 2>/dev/null` ; do
          if [ `uname` == "Darwin" ]; then
            fixMacOSBinary "$file" "$escapedBaseDir" '@loader_path/../lib' "$libPathLog"
          else
            chrpath -r "\${ORIGIN}/../lib" "$file" >> $libPathLog 2>&1
          fi
        done

        if [[ -d "$buildLocation/lib/postgresql" ]]; then
          cd $buildLocation/lib/postgresql
          for file in `ls -d $suffix 2>/dev/null` ; do
            if [ `uname` == "Darwin" ]; then
              fixMacOSBinary "$file" "$escapedBaseDir" '@loader_path/../../lib' "$libPathLog"
            else
              chrpath -r "\${ORIGIN}/../../lib" "$file" >> $libPathLog 2>&1
            fi
          done
        fi

	lib64=/usr/lib64
	shared_lib=$buildLocation/lib
	if [ "$comp" == "decoderbufs" ]; then
          cp -P $lib64/libproto*.so* $shared_lib/.
	elif [ "$comp" == "postgis" ]; then
          cp -P $lib64/libprotobuf*.so* $shared_lib/.
          cp -P $lib64/libgeos*.so*  $shared_lib/.
          cp -P $lib64/libgdal*.so*  $shared_lib/.
          cp -P $lib64/libproj*.so*  $shared_lib/.
          cp -P $lib64/libtiff*.so*  $shared_lib/.
          cp -P $lib64/libwebp.so*  $shared_lib/.
          cp -P $lib64/libjbig.so*  $shared_lib/.
          cp -P $lib64/libjpeg.so*  $shared_lib/.
        fi
}



function configureComp {
    rc=0

    make="make"

    if [ "$comp" == "citus" ]; then
        echo "# configure citus..."
        ./configure --enable-debug  --prefix=$buildLocation >> $make_log 2>&1 
        rc=$?
    fi

    if [ "$comp" == "backrest" ]; then
        echo "# configure backrest..."
        export LD_LIBRARY_PATH=$buildLocation/lib
        cd src
        ./configure --enable-debug --prefix=$buildLocation LDFLAGS="$LDFLAGS -Wl,-rpath,$sharedLibs" >> $make_log 2>&1 
        rc=$?
    fi

    if [ "$comp" == "psqlodbc" ]; then
        echo "# bootstrap psqlodbc..."
        ./bootstrap >> $make_log 2>&1
        rc=$?
        echo "# configure psqlodbc..."
        ./configure --prefix=$buildLocation >> $make_log 2>&1 
        rc=$?
    fi

    if [ "$comp" == "bouncer" ]; then
        echo "# configure bouncer..."
        opt="--prefix=$buildLocation --enable-debug --with-cares --with-pam --with-openssl --with-systemd"
        echo "#    $opt"
        ./configure $opt LDFLAGS="$LDFLAGS -Wl,-rpath,$sharedLibs -L$sharedLibs" > $make_log 2>&1
        rc=$?
    fi

    if [ "$comp" == "postgis" ]; then
        echo "# configure postgis..."
	export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
        ./configure --prefix=$buildLocation --without-raster --enable-debug LDFLAGS="$LDFLAGS -Wl,-rpath,$sharedLibs" > $make_log 2>&1
        rc=$?
    fi

    if [ ! "$rc" == "0" ]; then
       echo " "
       echo "ERROR: configureComp() failed, check make_log"
       echo " "
       tail -20 $make_log
       exit 1
    fi
}


function buildComp {
        comp="$1"
        echo "#        comp: $comp"
        shortV="$2"
        ##echo "#      shortV: $shortV"
        fullV="$3"
        echo "#       fullV: $fullV"
        buildV="$4"
        echo "#      buildV: $buildV"
        src="$5"
        echo "#         src: $src"

	echo "# PATH = $PATH"

        if [ "$comp" == "backrest" ] || [ "$comp" == "psqlodbc" ] || [ "$comp" == "bouncer" ]; then
            componentName="$comp$shortV-$fullV-$buildV-$buildOS"
        else
            componentName="$comp$shortV-pg$pgShortVersion-$fullV-$buildV-$buildOS"
        fi
        echo "#      compNm: $componentName"
        mkdir -p "$baseDir/$workDir/logs"
        cd "$baseDir/$workDir"
        rm -rf $comp
        mkdir $comp 
        cmd="tar -xzf $src --strip-components=1 -C $comp"
        echo "# $cmd"
        $cmd
        cd $comp

        buildLocation="$baseDir/$workDir/build/$componentName"

        prepComponentBuildDir $buildLocation

        PATH=$buildLocation/bin:$PATH
        log_dir="$baseDir/$workDir/logs"
        ##echo "#     log_dir: $log_dir"
        make_log="$log_dir/$comp-make.log"
        echo "#    make_log: $make_log"
        install_log="$log_dir/$comp-install.log"
        echo "# install_log: $install_log"

        configureComp

        make_install="make install"
        if [ "$comp" == "multicorn" ]; then
            make_install="sudo env "PATH=$PATH" make install"
            export PYTHON_OVERRIDE=python3.11
        fi

        echo "#  @`date`  make -j $CORES"
        USE_PGXS=1 $make -j $CORES >> $make_log 2>&1
        rc=$?
        echo "  rc = $rc"
        if [ "$rc" == "0" ] || [ "$comp" == "plv8" ]; then
                echo "#  @`date`  make install..."
                USE_PGXS=1 $make_install > $install_log 2>&1
                if [[ $? -ne 0 ]]; then
                        echo " "
                        echo "ERROR: Install failed, check install_log"
                        tail -20 $install_log
                        echo ""
                        return 1
                fi
        else
                echo " "
                echo "ERROR: Make failed, check make_log"
                echo " "
                tail -20 $make_log
                return 1
        fi

        if [ "$comp" == "multicorn" ]; then
          sudo chown $USER:$USER $buildLocation/lib/postgresql/multicorn.so
        fi

        componentBundle=$componentName
        cleanUpComponentDir $buildLocation
        updateSharedLibs $comp
        packageComponent $componentBundle
}


function buildPlJavaComponent {
	echo "# buildPlJavaComponent()"
	componentName="pljava$pljavaShortV-pg$pgShortVersion-$pljavaFullV-$pljavaBuildV-$buildOS"
	echo "# ComponentName = $componentName"
	mkdir -p "$baseDir/$workDir/logs"
	cd "$baseDir/$workDir"
	echo "#        Source = $Source"
	mkdir pljava && tar -xf $Source --strip-components=1 -C pljava
	cd pljava
	buildLocation="$baseDir/$workDir/build/$componentName"
	prepComponentBuildDir $buildLocation
	PATH=$buildLocation/bin:$PATH
	log=$baseDir/$workDir/logs/pljava_make.log
	echo "#      Make Log = $log"
	mvn clean install >> $log 2>&1
	rc=$?
 	if [ $rc == "0" ]; then
		log=$baseDir/$workDir/logs/pljava_install.log
		echo "#   Install Log = $log"
		jar="pljava-packaging/target/pljava-pg`echo $pgFullVersion | awk -F '.' '{print $1"."$2}'`-amd64-Linux-gpp.jar"
		echo "#           Jar = $jar"
 		java -jar $jar > $log 2>&1 > $log 2>&1
 		if [[ $? -ne 0 ]]; then
 			echo "Pl/Java install failed, check logs for details."
 		fi
 	else
                 mkdir -p pljava-packaging/target
                 cp "/tmp/pljava-pg`echo $pgFullVersion | awk -F '.' '{print $1}'`-amd64-Linux-gpp.jar" pljava-packaging/target/
                 java -jar "pljava-packaging/target/pljava-pg`echo $pgFullVersion | awk -F '.' '{print $1}'`-amd64-Linux-gpp.jar" > $baseDir/$workDir/logs/pljava_install.log 2>&1
 	fi

	componentBundle=$componentName
	cleanUpComponentDir $buildLocation
	updateSharedLibs
	packageComponent $componentBundle
}


function buildPlProfilerComponent {

	componentName="plprofiler$plProfilerShortVersion-pg$pgShortVersion-$plProfilerFullVersion-$plprofilerBuildV-$buildOS"
	mkdir -p "$baseDir/$workDir/logs"
	cd "$baseDir/$workDir"
	mkdir plprofiler && tar -xf $plProfilerSource --strip-components=1 -C plprofiler
	cd plprofiler

	buildLocation="$baseDir/$workDir/build/$componentName"

	prepComponentBuildDir $buildLocation

	PATH=$buildLocation/bin:$PATH
	USE_PGXS=1 make > $baseDir/$workDir/logs/plprofiler_make.log 2>&1
        if [[ $? -eq 0 ]]; then
        	USE_PGXS=1 make install > $baseDir/$workDir/logs/plprofiler_install.log 2>&1
                if [[ $? -ne 0 ]]; then
                                echo "Failed to install PlProfiler ..."
                fi
                mkdir -p $buildLocation/python/site-packages
                cd python-plprofiler
        	cp -R plprofiler $buildLocation/python/site-packages
        	#cp plprofiler-bin.py $buildLocation/bin/plprofiler
        	cd $buildLocation/python/site-packages
        	#tar -xf $psycopgSource
        else
        	echo "Make failed for PlProfiler .... "
        fi
        rm -rf build
	componentBundle=$componentName
	cleanUpComponentDir $buildLocation
	updateSharedLibs
	packageComponent $componentBundle
}




function buildTimeScaleDBComponent {

        componentName="timescaledb-pg$pgShortVersion-$timescaledbFullV-$timescaledbBuildV-$buildOS"
        echo "#   compNm: $componentName"
        mkdir -p "$baseDir/$workDir/logs"
        cd "$baseDir/$workDir"
        mkdir timescaledb && tar -xf $timescaleDBSource --strip-components=1 -C timescaledb
        cd timescaledb

        buildLocation="$baseDir/$workDir/build/$componentName"

        prepComponentBuildDir $buildLocation

        PATH=/opt/pgbin-build/pgbin/bin:$buildLocation/bin:$PATH

	bootstrap_log=$baseDir/$workDir/logs/timescaledb_bootstrap.log
	##./bootstrap -DAPACHE_ONLY=1 -DREGRESS_CHECKS=OFF > $bootstrap_log 2>&1
	./bootstrap -DREGRESS_CHECKS=OFF > $bootstrap_log 2>&1
        if [[ $? -ne 0 ]]; then
                echo "timescaledb Bootstrap failed, check logs for details."
                echo "  $bootstrap_log"
                return 1
        fi

	cd build
        make_log=$baseDir/$workDir/logs/timescaledb_make.log
        echo "#  @`date`  make -j $CORES"
        USE_PGXS=1 make -j $CORES -d > $make_log 2>&1
        if [[ $? -eq 0 ]]; then
                echo "#  @`date`  make install"
                USE_PGXS=1 make install > $baseDir/$workDir/logs/timescaledb_install.log 2>&1
                if [[ $? -ne 0 ]]; then
                        echo "timescaledb install failed, check logs for details."
                fi
        else
                echo "timescaledb Make failed, check logs for details."
                echo "  $make_log"
                return 1
        fi

        componentBundle=$componentName
        cleanUpComponentDir $buildLocation
        updateSharedLibs
        packageComponent $componentBundle
}

TEMP=`getopt -l no-tar, copy-bin,no-copy-bin,with-pgver:,with-pgbin:,build-curl:,build-hypopg:,build-postgis:,build-sqlitefdw:,build-orafce:,build-audit:,build-setuser:,build-permissions:,build-partman:,build-pldebugger:,build-pljava:,build-plv8:,build-plprofiler:,build-backrest:,build-spock33:,build-spock40:,build-snowflake:,build-wal2json:,build-hintplan:,build-timescaledb:,build-cron:,build-citus:,build-vector:,build-bouncer: -- "$@"`

if [ $? != 0 ] ; then
	echo "Required parameters missing, Terminating..."
	exit 1
fi

copyBin=false
compDir="$8"

while true; do
  case "$1" in
    --with-pgver ) pgVer=$2; shift; shift; ;;
    --with-pgbin ) pgBinPassed=true; pgBin=$2; shift; shift; ;;
    --target-dir ) targetDirPassed=true; targetDir=$2; shift; shift ;;
    --build-postgis ) buildPostGIS=true; Source=$2; shift; shift ;;
    --build-decoderbufs ) buildDecoderBufs=true Source=$2; shift; shift ;;
    --build-sqlitefdw ) buildSqliteFDW=true; Source=$2; shift; shift ;;
    --build-orafce ) buildOrafce=true; Source=$2; shift; shift ;;
    --build-audit ) buildAudit=true; Source=$2; shift; shift ;;
    --build-setuser ) buildSetUser=true; Source=$2; shift; shift ;;
    --build-permissions ) buildPermissions=true; Source=$2; shift; shift ;;
    --build-hypopg ) buildHypopg=true; Source=$2; shift; shift ;;
    --build-curl ) buildCurl=true; Source=$2; shift; shift ;;
    --build-pldebugger ) buildPLDebugger=true; Source=$2; shift; shift ;;
    --build-partman ) buildPartman=true; Source=$2; shift; shift ;;
    --build-plv8 ) buildPlV8=true; Source=$2; shift; shift ;;
    --build-pljava ) buildPlJava=true; Source=$2; shift; shift ;;
    --build-plprofiler ) buildPlProfiler=true; plProfilerSource=$2; shift; shift ;;
    --build-backrest ) buildBackrest=true; Source=$2; shift; shift ;;
    --build-bouncer ) buildBouncer=true; Source=$2; shift; shift ;;
    --build-snowflake ) buildSnowflake=true; Source=$2; shift; shift ;;
    --build-spock33 ) buildSpock33=true; Source=$2; shift; shift ;;
    --build-spock40 ) buildSpock40=true; Source=$2; shift; shift ;;
    --build-lolor )   buildLolor=true; Source=$2; shift; shift ;;
    --build-wal2json ) buildWal2Json=true; Source=$2; shift; shift ;;
    --build-hintplan ) buildHintPlan=true; Source=$2; shift; shift ;;
    --build-timescaledb ) buildTimeScaleDB=true; timescaleDBSource=$2; shift; shift ;;
    --build-cron ) buildCron=true; Source=$2; shift; shift ;;
    --build-multicorn ) buildMulticorn=true; Source=$2; shift; shift ;;
    --build-anon ) buildAnon=true; Source=$2; shift; shift ;;
    --build-ddlx ) buildDdlx=true; Source=$2; shift; shift ;;
    --build-citus ) buildCitus=true; Source=$2; shift; shift ;;
    --build-vector ) buildVector=true; Source=$2; shift; shift ;;
    --copy-bin ) copyBin=true; shift; shift; ;;
    --no-copy-bin ) copyBin=false; shift; shift; ;;
    --no-tar ) copyBin=false; noTar=true; shift; shift; ;;
    -- ) shift; break ;;
    -* ) echo "Invalid Option Passed"; exit 1; ;;
    * ) break ;;
  esac
done

if [[ $pgBinPassed != "true" ]]; then
	echo "Please provide a valid PostgreSQL version to build ..."
	exit 1
fi

getPGVersion

PGHOME=$pgBin

if [[ $buildOrafce == "true" ]]; then
	buildComp orafce "$orafceShortV" "$orafceFullV" "$orafceBuildV" "$Source"
fi

if [[ $buildDecoderBufs == "true" ]]; then
	export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
	buildComp decoderbufs "$decoderbufsShortV" "$decoderbufsFullV" "$decoderbufsBuildV" "$Source"
fi

if [[ $buildSqliteFDW == "true" ]]; then
#	echo "ORACLE_HOME=$ORACLE_HOME"
#	if [ ! "$ORACLE_HOME" > " " ]; then
#		echo "FATAL ERROR: ORACLE_HOME is not set"
#		exit 1
#	fi
	buildComp sqlitefdw "$sqlitefdwShortV" "$sqlitefdwFullV" "$sqlitefdwBuildV" "$Source"
fi

if [[ $buildPostGIS ==  "true" ]]; then
	buildComp postgis "$postgisShortV" "$postgisFullV" "$postgisBuildV" "$Source"
fi

if [[ $buildSetUser ==  "true" ]]; then
	buildComp setuser "$setuserShortV" "$setuserFullV" "$setuserBuildV" "$Source"
fi

if [[ $buildPermissions ==  "true" ]]; then
	buildComp permissions "$permissionsShortV" "$permissionsFullV" "$permissionsBuildV" "$Source"
fi

if [[ $buildAudit == "true" ]]; then
	if [ "$pgShortVersion" == "15" ]; then
		buildComp audit "$auditShortV" "$auditFull15V" "$auditBuildV" "$Source"
	elif [ "$pgShortVersion" == "16" ]; then
		buildComp audit "$auditShortV" "$auditFull16V" "$auditBuildV" "$Source"
	fi
fi

if [ "$buildCurl" == "true" ]; then
	buildComp curl "$curlShortV" "$curlFullV" "$curlBuildV" "$Source"
fi

if [ "$buildHypopg" == "true" ]; then
	buildComp hypopg "$hypopgShortV" "$hypopgFullV" "$hypopgBuildV" "$Source"
fi

if [ "$buildCron" == "true" ]; then
	buildComp cron  "$cronShortV" "$cronFullV" "$cronBuildV" "$Source"
fi

if [ "$buildMulticorn" == "true" ]; then
	buildComp multicorn  "$multicornShortV" "$multicornFullV" "$multicornBuildV" "$Source"
fi

if [[ $buildSnowflake == "true" ]]; then
	buildComp snowflake  "" "$snwflkV" "$snwflkBldV" "$Source"
fi

if [[ $buildWal2Json == "true" ]]; then
	buildComp wal2json  "" "$wal2jV" "$wal2jBldV" "$Source"
fi

if [[ $buildSpock33 == "true" ]]; then
	buildComp spock33  "" "$spock33V" "$spockBld33V" "$Source"
fi

if [[ $buildSpock40 == "true" ]]; then
	buildComp spock40  "" "$spock40V" "$spockBld40V" "$Source"
fi

if [[ $buildLolor == "true" ]]; then
	buildComp lolor  "" "$lolorV" "$lolorBldV" "$Source"
fi

if [[ $buildPLDebugger == "true" ]]; then
	buildComp pldebugger  "$debugShortV" "$debugFullV" "$debugBuildV" "$Source"
fi

if [[ $buildPartman == "true" ]]; then
	buildComp partman "$partmanShortV" "$partmanFullV" "$partmanBuildV" "$Source"
fi

if [[ $buildPlJava == "true" ]]; then
	buildPlJavaComponent
fi

if [[ $buildPlV8 == "true" ]]; then
	buildComp plv8  "$plv8ShortV" "$plv8FullV" "$plv8BuildV" "$Source"
fi

if [[ $buildPlProfiler == "true" ]]; then
	buildPlProfilerComponent
fi

if [[ $buildBackrest == "true" ]]; then
	buildComp backrest "$backrestShortV" "$backrestFullV" "$backrestBuildV" "$Source"
fi

if [[ $buildBouncer == "true" ]]; then
	buildComp bouncer  "" "$bouncerV" "$bouncerBldV" "$Source"
fi

if [[ $buildHintPlan == "true" ]]; then
	if [ "$pgShortVersion" == "15" ]; then
		buildComp hintplan "$hintplanShortV" "$hintplan15V" "$hintplanBuildV" "$Source"
	elif [ "$pgShortVersion" == "16" ]; then
		buildComp hintplan "$hintplanShortV" "$hintplan16V" "$hintplanBuildV" "$Source"
	elif [ "$pgShortVersion" == "17" ]; then
		buildComp hintplan "$hintplanShortV" "$hintplan17V" "$hintplanBuildV" "$Source"
	fi
fi

if [[ $buildTimeScaleDB == "true" ]]; then
	buildTimeScaleDBComponent
fi

if [[ $buildAnon == "true" ]]; then
	buildComp anon "$anonShortV" "$anonFullV" "$anonBuildV" "$Source"
fi

if [[ $buildDdlx == "true" ]]; then
	buildComp ddlx "$ddlxShortV" "$ddlxFullV" "$ddlxBuildV" "$Source"
fi

if [ "$buildCitus" == "true" ]; then
	buildComp citus "$citusShortV" "$citusFullV" "$citusBuildV" "$Source"
fi

if [ "$buildVector" == "true" ]; then
	buildComp vector "$vectorShortV" "$vectorFullV" "$vectorBuildV" "$Source"
fi

destDir=`date +%Y-%m-%d`
fullDestDir=/opt/pgbin-builds/$destDir

exit 0

