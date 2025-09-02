#!/bin/bash
set -e

DB_NAME="appdb"
DB_USER="appuser"
DB_PASS="{{DB_PASSWORD}}"  # Replace with Pulumi secret

# Save password securely
echo "MySQL password for $DB_USER: $DB_PASS" > /root/db_password.txt
chmod 600 /root/db_password.txt

# Update system and install prerequisites
yum update -y
yum install -y yum-utils

# Add official MySQL repo
rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-11.noarch.rpm
yum-config-manager --enable mysql80-community

# Install MySQL server
yum install -y mysql-community-server

# Enable and start MySQL
systemctl enable mysqld
systemctl start mysqld
sleep 5  # wait for MySQL to fully initialize

# Get temporary root password
TEMP_PASS=$(grep 'temporary password' /var/log/mysqld.log | awk '{print $NF}')

# Set permanent root password using mysql_native_password
mysql --connect-expired-password -uroot -p"${TEMP_PASS}" <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
FLUSH PRIVILEGES;
EOF

# Configure bind address to allow remote connections
sed -i "s/^bind-address.*/bind-address=0.0.0.0/" /etc/my.cnf
systemctl restart mysqld
sleep 5

# Create database and appuser
mysql -uroot -p"${DB_PASS}" <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};

-- App user accessible from any host (%)
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'%';

-- App user accessible locally
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';

FLUSH PRIVILEGES;
EOF

echo "MySQL setup complete. Database: $DB_NAME, User: $DB_USER"
