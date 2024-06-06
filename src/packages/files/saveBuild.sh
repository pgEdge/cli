#!/bin/bash

printf "\n\n"
printf "====================\n"
printf "$0 Now executing... \n\n"

printf "Mounts currently installed:\n"
df -h

while [ -n "$1" ]
do
    case "$1" in
        --saveDir )
            shift
            saveDir="$1"
            shift
        ;;
        --platform)
            shift
            platform="$1"
            shift
        ;;
        --inputDir )
            shift
            inputDir="$1"
            shift
        ;;
            
    esac
done

if [ -z "$saveDir" -o -z "$platform" -o -z "$inputDir" ] 
then
    printf "You must supply all options:\n"
    printf "\t$0 --saveDir <dir> --platform <platform_name> --inputDir <dir>\n"
    printf "\t$0 --saveDir /build/output --platform el7 --inputDir /tmp/build\n"
    exit 1
fi

dt=`date '+%Y%m%d'`
currTime=`date '+%s'`

thisBuildDir=$saveDir/$platform/$dt/$currTime
printf "\tWill save build in: $thisBuildDir\n"

test -d $thisBuildDir
if [ "$?" -ne 0 ] 
then
    printf "\tDoes not exist, creating: $thisBuildDir\n"
    mkdir -p $thisBuildDir
fi

printf "\tCopying builds from $inputDir to $thisBuildDir\n"
rsync -avzP $inputDir/* $thisBuildDir/    

printf "$0 Now Completed... \n"
printf "BuildOutputSentTo: $thisBuildDir/\n\n"
printf "====================\n\n"
