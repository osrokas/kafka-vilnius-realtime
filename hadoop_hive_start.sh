# Run hadoop services
start-dfs.sh
start-yarn.sh

sleep 2

# Run Hive
hive --service metastore &
sleep 2
hive --service hiveserver2 &