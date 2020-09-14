#!/usr/bin/bash


# Hoistied functions:
function getSub {
     local consprod=$1
     if [[ $consprod == *"consumer"* ]]; then
	 SUB="Consumer"
     else
	 SUB="Producer"
     fi
}	     

function getFmt {
    local fmt=$1
    if [[ $fmt == *"grpc"* ]]; then
	FMT="gRPC"
    else
	FMT="Kafka"
    fi
}
# End of hoisties


VERSION=$1

if (( $# > 1)); then
    # Only perform on the provided images:
    for i in ${@:2}
    do
	 i=${i//,}
	 echo "Running for ${i}"
         getSub "$i"
	 getFmt "$i"	 
    	 docker build -f Dockerfiles/$SUB/$FMT/Dockerfile -t $i . && \
	 docker tag $i eliharper/$i:$VERSION && \
	 docker push eliharper/$i:$VERSION
    done
    exit 0
fi

images=("grpc_consumer", "grpc_producer", "kafka_consumer", "kafka_producer")
echo "RUNNING FOR ALL!"

for i in "${images[@]}"
do
     i=${i//,}
     getSub $i
	 getFmt $i
	 docker build -f Dockerfiles/$SUB/$FMT/Dockerfile -t ${i//,} . && \
	 docker tag $i eliharper/$i:$VERSION && \
	 docker push eliharper/$i:$VERSION
	 
done

