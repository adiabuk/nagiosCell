#!/bin/bash

port=$1

value=`netstat -na |grep ESTAB|awk {'print $4'}|grep ${port}$|wc -l`
[[ -n $port ]] && myport=$echo "on port $port"
echo "$value connections ESTABLISHED $myport|connections=$value;20000;40000;0;50000"
