#!/bin/bash

# Run hadoop services
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

sleep 2

# Run Hive
hive --service metastore &
sleep 2
hive --service hiveserver2 &