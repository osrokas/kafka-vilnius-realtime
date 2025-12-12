# Complete Big Data Stack Setup Guide
## Hadoop 3.4.1 + Spark 3.5.4 + Hive 4.1.0 + Iceberg 1.7.1 on Ubuntu

---

## Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y wget tar ssh pdsh openssh-server openssh-client
```

---

## 1. Install Java 17

```bash
# Install OpenJDK 17
sudo apt install -y openjdk-17-jdk

# Verify installation
java -version

# Set JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## 2. Create Hadoop User (Optional but Recommended)

```bash
# Create hadoop user
sudo adduser hadoop
sudo usermod -aG sudo hadoop

# Switch to hadoop user
su - hadoop
```

---

## 3. Configure SSH (for Hadoop)

```bash
# Generate SSH key (press Enter for all prompts)
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa

# Add to authorized keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

# Test SSH
ssh localhost
exit
```

---

## 4. Install Hadoop 3.4.1

```bash
# Download Hadoop
cd ~
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz

# Extract and move
tar -xzf hadoop-3.4.1.tar.gz
sudo mv hadoop-3.4.1 /usr/local/hadoop
sudo chown -R $USER:$USER /usr/local/hadoop

# Set environment variables
cat >> ~/.bashrc << 'EOF'

# Hadoop Environment
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
EOF

source ~/.bashrc
```

### Configure Hadoop

```bash
# Edit hadoop-env.sh
echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

**Create core-site.xml:**

```bash
cat > $HADOOP_HOME/etc/hadoop/core-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/home/hadoop/hadoopdata/tmp</value>
    </property>
    <property>
        <name>hadoop.proxyuser.hadoop.groups</name>
        <value>*</value>
    </property>
    <property>
        <name>hadoop.proxyuser.hadoop.hosts</name>
        <value>*</value>
    </property>
</configuration>
EOF
```

**Create hdfs-site.xml:**

```bash
cat > $HADOOP_HOME/etc/hadoop/hdfs-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///home/hadoop/hadoopdata/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///home/hadoop/hadoopdata/hdfs/datanode</value>
    </property>
</configuration>
EOF
```

**Create mapred-site.xml:**

```bash
cat > $HADOOP_HOME/etc/hadoop/mapred-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
EOF
```

**Create yarn-site.xml:**

```bash
cat > $HADOOP_HOME/etc/hadoop/yarn-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
EOF
```

### Initialize and Start Hadoop

```bash
# Create directories
mkdir -p ~/hadoopdata/hdfs/namenode
mkdir -p ~/hadoopdata/hdfs/datanode
mkdir -p ~/hadoopdata/tmp

# Format HDFS
hdfs namenode -format

# Start Hadoop
start-dfs.sh
start-yarn.sh

# Verify services are running
jps
# Should show: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager

# Access web interfaces:
# NameNode: http://localhost:9870
# ResourceManager: http://localhost:8088
```

---

## 5. Install Spark 3.5.4

```bash
# Download Spark
cd ~
wget https://downloads.apache.org/spark/spark-3.5.4/spark-3.5.4-bin-hadoop3.tgz

# Extract and move
tar -xzf spark-3.5.4-bin-hadoop3.tgz
sudo mv spark-3.5.4-bin-hadoop3 /usr/local/spark
sudo chown -R $USER:$USER /usr/local/spark

# Set environment variables
cat >> ~/.bashrc << 'EOF'

# Spark Environment
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF

source ~/.bashrc
```

### Configure Spark

```bash
# Create spark-env.sh
cat > $SPARK_HOME/conf/spark-env.sh << 'EOF'
#!/usr/bin/env bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop
export SPARK_MASTER_HOST=localhost
export PYSPARK_PYTHON=/usr/bin/python3
EOF

chmod +x $SPARK_HOME/conf/spark-env.sh

# Create spark-defaults.conf
cat > $SPARK_HOME/conf/spark-defaults.conf << 'EOF'
spark.master                     spark://localhost:7077
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://localhost:9000/spark-logs
spark.history.fs.logDirectory    hdfs://localhost:9000/spark-logs
spark.serializer                 org.apache.spark.serializer.KryoSerializer
spark.driver.memory              2g
spark.executor.memory            2g
EOF

# Create HDFS directory for Spark logs
hdfs dfs -mkdir -p /spark-logs

# Test Spark
spark-shell --version
```

---

## 6. Install Hive 4.1.0

```bash
# Download Hive
cd ~
wget https://downloads.apache.org/hive/hive-4.1.0/apache-hive-4.1.0-bin.tar.gz

# Extract and move
tar -xzf apache-hive-4.1.0-bin.tar.gz
sudo mv apache-hive-4.1.0-bin /usr/local/hive
sudo chown -R $USER:$USER /usr/local/hive

# Set environment variables
cat >> ~/.bashrc << 'EOF'

# Hive Environment
export HIVE_HOME=/usr/local/hive
export PATH=$PATH:$HIVE_HOME/bin
export HIVE_CONF_DIR=$HIVE_HOME/conf
EOF

source ~/.bashrc

```

### Configure Hive

```bash
# Create HDFS directories for Hive
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -mkdir -p /tmp/hive
hdfs dfs -chmod g+w /user/hive/warehouse
hdfs dfs -chmod g+w /tmp/hive

# Download PostgreSQL connector (for Hive metastore)
cd /tmp
wget https://jdbc.postgresql.org/download/postgresql-42.7.1.jar
cp postgresql-42.7.1.jar $HIVE_HOME/lib/

# Or use Derby (embedded database for testing)
# Derby is included with Hive by default
```

**Create hive-site.xml:**

```bash
cat > $HIVE_HOME/conf/hive-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <!-- Hive Metastore -->
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:postgresql://localhost:5432/metastore_db</value>
        <description>JDBC connect string for PostgreSQL</description>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.postgresql.Driver</value>
        <description>JDBC driver class for PostgreSQL</description>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionUserName</name>
        <value>postgres</value>
        <description>PostgreSQL username</description>
    </property>
    
    <property>
        <name>javax.jdo.option.ConnectionPassword</name>
        <value>postgres</value>
        <description>PostgreSQL password</description>
    </property>
    
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>
    
    <property>
        <name>hive.metastore.uris</name>
        <value>thrift://localhost:9083</value>
    </property>
    
    <!-- Execution Engine -->
    <property>
        <name>hive.execution.engine</name>
        <value>tez</value>
    </property>
    
    <!-- HiveServer2 -->
    <property>
        <name>hive.server2.thrift.port</name>
        <value>10000</value>
    </property>
    
    <property>
        <name>hive.server2.webui.port</name>
        <value>10002</value>
    </property>
    
    <!-- Enable Iceberg -->
    <property>
        <name>iceberg.engine.hive.enabled</name>
        <value>true</value>
    </property>
</configuration>
EOF
```

**Create hive-env.sh:**

```bash
cat > $HIVE_HOME/conf/hive-env.sh << 'EOF'
export HADOOP_HOME=/usr/local/hadoop
export HIVE_CONF_DIR=/usr/local/hive/conf
export HIVE_AUX_JARS_PATH=/usr/local/hive/lib
EOF
```

### Install Tez (Optional - for better performance)

```bash
# Download Tez 0.10.5
cd ~
wget https://downloads.apache.org/tez/0.10.5/apache-tez-0.10.5-bin.tar.gz
tar -xzf apache-tez-0.10.5-bin.tar.gz
sudo mv apache-tez-0.10.5-bin /usr/local/tez

# Upload Tez to HDFS
hdfs dfs -mkdir -p /apps/tez
hdfs dfs -put /usr/local/tez/share/tez.tar.gz /apps/tez/

# Add Tez configuration to hive-site.xml
# (Add this property to your hive-site.xml)
cat >> $HIVE_HOME/conf/hive-site.xml << 'EOF'
    <property>
        <name>tez.lib.uris</name>
        <value>${fs.defaultFS}/apps/tez/tez.tar.gz</value>
    </property>
</configuration>
EOF

# Note: Remove the duplicate </configuration> tag at the end
```

### Initialize Hive Metastore

```bash
# Connect to PostgreSQL and create metastore database
sudo -u postgres psql
CREATE DATABASE metastore_db;

# Initialize schema
schematool -dbType postgres -initSchema

# Start Hive Metastore
hive --service metastore &

# Start HiveServer2
hive --service hiveserver2 &

# Test Hive
beeline -u "jdbc:hive2://localhost:10000/default;user=hadoop"

# In beeline:
# CREATE DATABASE test;
# SHOW DATABASES;
# !quit
```

---

## 7. Install Apache Iceberg 1.7.1

Iceberg integrates with Spark and Hive through runtime JARs.

### For Spark 3.5 + Iceberg 1.7.1

```bash
# Download Iceberg Spark runtime
cd ~
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.13/1.7.1/iceberg-spark-runtime-3.5_2.13-1.7.1.jar

# Copy to Spark jars
cp iceberg-spark-runtime-3.5_2.13-1.7.1.jar $SPARK_HOME/jars/
```

### For Hive + Iceberg 1.7.1

```bash
# Download Iceberg Hive runtime
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-hive-runtime/1.7.1/iceberg-hive-runtime-1.7.1.jar

# Copy to Hive lib
cp iceberg-hive-runtime-1.7.1.jar $HIVE_HOME/lib/
```

### Configure Spark for Iceberg

**Update spark-defaults.conf:**

```bash
cat >> $SPARK_HOME/conf/spark-defaults.conf << 'EOF'

# Iceberg Configuration
spark.sql.extensions                              org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.spark_catalog                   org.apache.iceberg.spark.SparkSessionCatalog
spark.sql.catalog.spark_catalog.type              hive
spark.sql.catalog.local                           org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.local.type                      hadoop
spark.sql.catalog.local.warehouse                 hdfs://localhost:9000/user/iceberg/warehouse
EOF

# Create Iceberg warehouse directory
hdfs dfs -mkdir -p /user/iceberg/warehouse
```

---

## 8. Testing the Complete Stack

### Test Hadoop

```bash
# HDFS test
hdfs dfs -ls /
hdfs dfs -mkdir /test
echo "Hello Hadoop" > test.txt
hdfs dfs -put test.txt /test/
hdfs dfs -cat /test/test.txt
```

### Test Spark

```bash
# Start Spark shell
spark-shell

# Run Scala test
val data = Seq(1, 2, 3, 4, 5)
val distData = sc.parallelize(data)
distData.reduce(_ + _)
// Should output: 15

:quit
```

### Test PySpark

```bash
# Install Python and PySpark
sudo apt install -y python3 python3-pip
pip3 install pyspark==3.5.4

# Start PySpark
pyspark

# Run Python test
data = [1, 2, 3, 4, 5]
distData = sc.parallelize(data)
distData.reduce(lambda a, b: a + b)
# Should output: 15

exit()
```

### Test Hive

```bash
# Connect to HiveServer2
beeline -u jdbc:hive2://localhost:10000

# Create test table
CREATE TABLE employees (
    id INT,
    name STRING,
    dept STRING
);

INSERT INTO employees VALUES (1, 'John', 'IT'), (2, 'Jane', 'HR');

SELECT * FROM employees;

!quit
```

### Test Iceberg with Spark

```bash
# Start Spark SQL
spark-sql

# Create Iceberg table
CREATE TABLE local.db.iceberg_test (
    id INT,
    name STRING,
    value DOUBLE
) USING iceberg;

INSERT INTO local.db.iceberg_test VALUES (1, 'test', 100.0);

SELECT * FROM local.db.iceberg_test;

-- Test time travel
SELECT * FROM local.db.iceberg_test VERSION AS OF 1;

-- Show table history
SELECT * FROM local.db.iceberg_test.history;

EXIT;
```

### Test Iceberg with Hive

```bash
beeline -u jdbc:hive2://localhost:10000

# Create Iceberg table in Hive
CREATE TABLE iceberg_hive_test (
    trip_id BIGINT,
    trip_distance FLOAT,
    fare_amount DOUBLE
)
PARTITIONED BY (vendor_id BIGINT)
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler';

INSERT INTO iceberg_hive_test VALUES (1, 5.5, 15.0, 101);

SELECT * FROM iceberg_hive_test;

!quit
```

---

## 9. Useful Commands

### Start All Services

```bash
# Start Hadoop
start-dfs.sh
start-yarn.sh

# Start Hive Metastore
nohup hive --service metastore > /tmp/metastore.log 2>&1 &

# Start HiveServer2
nohup hive --service hiveserver2 > /tmp/hiveserver2.log 2>&1 &
```

### Stop All Services

```bash
# Stop Hadoop
stop-yarn.sh
stop-dfs.sh

# Stop Hive services
pkill -f HiveMetaStore
pkill -f HiveServer2
```

### Check Running Services

```bash
jps
# Should show:
# - NameNode
# - DataNode
# - SecondaryNameNode
# - ResourceManager
# - NodeManager
# - RunJar (if Hive services are running)
```

---

## 10. Web UI Access

- **HDFS NameNode**: http://localhost:9870
- **YARN ResourceManager**: http://localhost:8088
- **Spark Master**: http://localhost:8080 (if standalone mode)
- **Spark History Server**: http://localhost:18080 (after starting)
- **HiveServer2 Web UI**: http://localhost:10002

---

## 11. Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Check ports
sudo netstat -tulpn | grep -E '9000|9870|8088|10000|10002'
# Kill process using the port
sudo kill -9 <PID>
```

**2. Permission denied in HDFS:**
```bash
hdfs dfs -chmod -R 777 /user/hive/warehouse
hdfs dfs -chmod -R 777 /tmp/hive
```

**3. Java version conflicts:**
```bash
# Ensure Java 17 is the default
sudo update-alternatives --config java
```

**4. Hadoop safe mode:**
```bash
# Leave safe mode
hdfs dfsadmin -safemode leave
```

**5. Metastore connection errors:**
```bash
# Reinitialize metastore
rm -rf ~/metastore_db
schematool -dbType derby -initSchema
```

---

## 12. Production Considerations

For production environments:

1. **Use PostgreSQL or MySQL** instead of Derby for Hive Metastore
2. **Configure proper security** (Kerberos authentication)
3. **Set up multi-node cluster** instead of single-node
4. **Configure resource limits** properly in YARN
5. **Enable High Availability** for NameNode
6. **Set up monitoring** (Prometheus, Grafana)
7. **Configure backup strategies** for metadata

---

## Version Compatibility Summary

| Component | Version | Java | Notes |
|-----------|---------|------|-------|
| Java      | 17      | -    | LTS version |
| Hadoop    | 3.4.1   | 17   | Latest stable |
| Spark     | 3.5.4   | 17   | Compatible with Hadoop 3.x |
| Hive      | 4.1.0   | 17   | Works with Hadoop 3.4.1, Tez 0.10.5 |
| Iceberg   | 1.7.1   | 11+  | Supports Spark 3.5 and Hive 4.x |
| Tez       | 0.10.5  | 11+  | Optional, for Hive performance |

---

## Alternative: Spark 4.0.1 Setup

If you want to use Spark 4 (latest major version):

```bash
# Download Spark 4.0.1
wget https://downloads.apache.org/spark/spark-4.0.1/spark-4.0.1-bin-hadoop3.tgz
tar -xzf spark-4.0.1-bin-hadoop3.tgz
sudo mv spark-4.0.1-bin-hadoop3 /usr/local/spark

# Use Iceberg runtime for Spark 4.0
wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/1.7.1/iceberg-spark-runtime-4.0_2.13-1.7.1.jar
cp iceberg-spark-runtime-4.0_2.13-1.7.1.jar $SPARK_HOME/jars/
```

**Note:** Spark 4 uses Scala 2.13 only and requires Java 17 or 21.

---

This completes the full setup! You now have a working big data stack with Hadoop, Spark, Hive, and Iceberg.