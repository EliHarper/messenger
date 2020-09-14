#!/usr/bin/bash


if (( $# < 1)); then
    echo "No argument specified. Try running with \"kafka\" as an argument to run the Kafka benchmark."
    FMT="gRPC"
elif [[ $1 == *"k"* ]]; then
        FMT="Kafka"
elif [[ $1 == *"g"* ]]; then
        FMT="gRPC"    
else
    echo "Argument not recognized; try again with \"gRPC\" or \"kafka\"."
fi


hosty=$(hostname)
if [[ $hosty == *"ocke"* ]]; then
    printf "\n\nrunning from docker!\n\n"
    WORKDIR=/home/eli.harper/messenger
    SUB="Consumer"
    INVOC="python3"
    if [[ $FMT == *"gRPC"* ]]; then
        FILESUF="_Server"
    else
        FILESUF='_consumer'
    fi
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
