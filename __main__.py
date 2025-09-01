"""AWS Hands-On Exam (Pulumi)"""

import pulumi
from pulumi_aws import ec2

# Get value from Config file
config = pulumi.Config()
vpc_cidr = config.require("vpcCidr")
public_subnet_cidr = config.require("publicSubnetCidr")
private_subnet_cidr = config.require("privateSubnetCidr")

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
