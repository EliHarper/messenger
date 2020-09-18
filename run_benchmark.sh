#!/usr/bin/bash


if (( $# < 1)); then
    echo "No argument specified. Try running with \"kafka\"  or \"pulsar\" as an argument"
    FMT="gRPC"
elif [[ $1 == *"afk"* ]]; then
        FMT="Kafka"
elif [[ $1 == *"uls"* ]]; then
    FMT="Pulsar"
elif [[ $1 == *"g"* ]]; then
        FMT="gRPC"    
else
    echo "Argument not recognized; try again with \"gRPC\" or \"kafka\"."
fi


hosty=$(hostname)
if [[ $hosty == *"ocke"* ]]; then
    printf "\n\nrunning from docker!\n\n"
    WORKDIR=/home/eli.harper/messenger
    INVOC="python3"
    SUB="Consumer"
    if [[ $FMT == *"gRPC"* ]]; then
        FILESUF="_Server"
    else
        FILESUF='_consumer'
    fi
    
elif [[ $hosty == *"enkin"* ]]; then
    printf "\n\nrunning from jenkins!\n\n"
    
    # Easy one; jenkins is only used as the Pulsar producer:
    WORKDIR=/home/eli.harper/messenger
    INVOC="python3"
    SUB="Producer"
    FILESUF="_producer"
else
    WORKDIR=/c/Users/eli.harper/Projects/Messenger
    SUB="Producer"
    INVOC="python"
    if [[ $FMT == *"gRPC"* ]]; then
        FILESUF="_Client"
    else
        FILESUF="_producer"
    fi
fi


cd $WORKDIR && pwd ; source env/bin/activate
tail -f $WORKDIR/log/$FMT$FILESUF.log &

MODULE=$SUB.$FMT."${FMT,,}""${FILESUF,,}"
printf "Executing: $MODULE"
$INVOC -m $MODULE

# kill $!
