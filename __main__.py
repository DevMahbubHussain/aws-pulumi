"""AWS Hands-On Exam (Pulumi)"""

import pulumi
from pulumi_aws import ec2
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Task 1 — Create a Secure VPC

# Get value from Config file
config = pulumi.Config()
vpc_cidr = config.require("vpcCidr")
public_subnet_cidr = config.require("publicSubnetCidr")
private_subnet_cidr = config.require("privateSubnetCidr")
instance_type = config.require("instanceType")

# Create vpc
vpc = ec2.Vpc(
    "main-vpc",
    cidr_block=vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "main-vpc", "Environment": "dev", "ManagedBy": "pulumi"},
)

# Create Public Subnet
public_subnet = ec2.Subnet(
    "public-subnet",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidr,
    map_public_ip_on_launch=True,
    availability_zone="ap-southeast-1a",
    tags={"Name": "public-subnet", "Environment": "dev", "Tier": "public"},
)


# Create Private Subnet
private_subnet = ec2.Subnet(
    "private-subnet",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidr,
    map_public_ip_on_launch=True,
    availability_zone="ap-southeast-1a",
    tags={"Name": "private-subnet", "Environment": "dev", "Tier": "private"},
)

# Create Internat Gateway
igw = ec2.InternetGateway(
    "main-igw", vpc_id=vpc.id, tags={"Name": "main-igw", "Environment": "dev"}
)


# Create Public Route Table
public_route_table = ec2.RouteTable(
    "public-route-table",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "gateway_id": igw.id}],
    tags={"Name": "public-route-table", "Environment": "dev"},
)

# Associate Public Route Table with Public Subnet
public_route_table_associate_public_subnet = ec2.RouteTableAssociation(
    "public-route-assoc",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id,
)


# Create an Elastic IP for the NAT Gateway
nat_eip = ec2.Eip(
    "nat-eip", domain="vpc", tags={"Name": "nat-eip", "Environment": "dev"}
)

# NAT Gateway in Public Subnet + Elastic IP for NatGateWay
nat_gateway = ec2.NatGateway(
    "nat-gateway",
    allocation_id=nat_eip.id,
    subnet_id=public_subnet.id,
    tags={"Name": "nat-gateway", "Environment": "dev"},
)


# Create Pribate Route Table
private_route_table = ec2.RouteTable(
    "private-route-table",
    vpc_id=vpc.id,
    routes=[{"cidr_block": "0.0.0.0/0", "nat_gateway_id": nat_gateway.id}],
    tags={"Name": "public-route-table", "Environment": "dev"},
)

# Associate Private Route Table with Private Subnet
private_route_table_associate_private_subnet = ec2.RouteTableAssociation(
    "private-route-assoc",
    subnet_id=private_subnet.id,
    route_table_id=private_route_table.id,
)
pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("private_subnet_id", private_subnet.id)
pulumi.export("internat_gatway_id", igw.id)
pulumi.export("public_route_table_id", public_route_table.id)
pulumi.export("private_route_table_id", private_route_table.id)
pulumi.export("nat_gateway_id", nat_gateway.id)


# Task 2 — Bastion Host in Public Subnet
# Generate RSA key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)
public_key = (
    private_key.public_key()
    .public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    .decode()
)

# Create KeyPair in AWS using the generated public key
key_pair = ec2.KeyPair(
    "dynamic-keypair",
    key_name="dynamic-keypair",
    public_key=public_key,
    tags={"Name": "dynamic-keypair", "Environment": "dev"},
)

# User data for hardening
user_data = f"""#!/bin/bash
# Create non-root user
useradd -m -s /bin/bash ops
mkdir -p /home/ops/.ssh
echo "{public_key}" > /home/ops/.ssh/authorized_keys
chown -R ops:ops /home/ops/.ssh
chmod 700 /home/ops/.ssh
chmod 600 /home/ops/.ssh/authorized_keys

# Allow sudo without password
echo "ops ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Harden SSH settings
sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
"""

# Export private key so you can SSH later
pulumi.export("key_pair_name", key_pair.key_name)
pulumi.export("private_key_material", private_key_pem.decode())


#  Security Groups
#  Public Security Group (for public instance)
bastion_sg = ec2.SecurityGroup(
    "bastion-sg",
    vpc_id=vpc.id,
    description="Security group for public EC2 instance",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "SSH access",
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "HTTP access",
        },
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}
    ],
    tags={"Name": "bastion-sg", "Environment": "dev"},
)


# AMI
ami = ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}],
).id

# Create EC2 Instance in Public Subnet
public_instance = ec2.Instance(
    "bastion-instance",
    ami=ami,
    instance_type=instance_type,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=bastion_sg.id,
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    user_data=user_data,
    tags={"Name": "bastion-instance", "Environment": "dev", "Tier": "public"},
)


pulumi.export("bastionPublicIp", public_instance.public_ip)


# Task 3 — Private EC2 Instance

# Private EC2 Security Group
app_sg = ec2.SecurityGroup(
    "app_sg ",
    vpc_id=vpc.id,
    description="Allow SSH only from Bastion Host",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "SSH access",
            # allow SSH only from bastion SG
            "security_groups": [bastion_sg.id],
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "SSH access from Bastion",
        },
    ],
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}
    ],
    tags={"Name": "app-sg", "Environment": "dev"},
    opts=pulumi.ResourceOptions(depends_on=[bastion_sg]),
)

# Create EC2 Instance in Private Subnet
private_instance = ec2.Instance(
    "private-instance",
    ami=ami,
    instance_type=instance_type,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[app_sg.id],
    associate_public_ip_address=False,
    key_name=key_pair.key_name,
    tags={"Name": "private-instance", "Environment": "dev", "Tier": "private"},
    opts=pulumi.ResourceOptions(depends_on=[public_instance]),
)

pulumi.export("privateInstancePrivateIp", private_instance.id)
