### **AWS Hands-On Exam (Pulumi)**


### Task 1 — Create a Secure VPC

This project uses **Pulumi** with **Python** to create a basic AWS networking setup, including:
- VPC
- Public and Private Subnets
- Internet Gateway (IGW)
- NAT Gateway
- Public and Private Route Tables


Task1: Create a Secure VPC

Task1:
![pulumi-preview](images/task1/pulumi-preview.png)
![pulumi-up](images/task1/pulumi-up.png)
![pulumi-stack](images/task1/pulumi-stack.png)
![stackjson](images/task1/stackjson.png)



### Task 2 — Bastion Host in Public Subnet

- EC2 in the public subnet with a public IPv4
- Security Group (bastion-sg): allow inbound TCP/22 only from your public IP.
- System hardening basics via User Data

Task2: Bastion Host in Public Subnet

![pulumi-stack](images/task2/pulumi-stack.png)
![SSH-session](images/task2/SSH-session.png)


### Task 3 — Private EC2 Instance

- EC2 in private subnet, SG (app-sg) must allow inbound SSH (22) only from bastion-sg (security group reference), not from the internet.

Task3: Private EC2 Instance

![SSH-session](images/task3/ssh.png)
![SSH-session](images/task3/sshs.png) 


### Task 4 — Install & Manage MySQL with systemd

- Use User Data (cloud-init) or a remote‑command provisioner to:
- Installed MySQL (community server) or MariaDB (acceptable).
- Configured to listen on 127.0.0.1 and the instance’s private IP.
- Created a database appdb and user appuser with a generated password.

Task4: 

![mysql](images/task4/mysql.png)
![maridbstatus](images/task4/maridbstatus.png)


### Task 5 — End‑to‑End Connectivity Validation

- From bastion → private instance: SSH works.
- From private instance → internet: curl https://aws.amazon.com works (via NAT).
- From bastion → MySQL on private instance.


Task5: 

![pingprivatetobastion](images/task5/pingprivatetobastion.png)
![pingpublictoprivate](images/task5/pingpublictoprivate.png)
![curl](images/task5/curl.png)


### Task 6 — Clean Infrastructure Teardown
- Show pulumi destroy output completing without orphaned resources.

Task6: 

![destroy2](images/task6/destroy2.png)


# Key Management on Windows Machine

```bash
### 1. Save Your Private Key Locally
pulumi stack output private_key_material > dynamic-key.pem

### 2. Convert to Linux Format
```bash
dos2unix dynamic-key.pem

### 3. Set Permissions
```bash
chmod 400 dynamic-key.pem

### 4. SSH into the Public (Bastion) Instance
```bash
ssh -i dynamic-key.pem ops@<bastionPublicIP>


# Access Private Instance via Bastion

### 1. Copy the Private Key to the Public EC2

```bash
scp -i dynamic-key.pem dynamic-key.pem ops@<bastionPublicIP>:~

### 2. Set Permissions on the Bastion
```bash
chmod 400 ~/dynamic-key.pem

### 3. SSH into the Private EC2 Using the Key
```bash
ssh -i ~/dynamic-key.pem ec2-user@<privateInstanceIP>

```

## 🛠️ **Prerequisites**
- [Python 3.8+](https://www.python.org/)
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) (configured with credentials)
- An AWS account with permissions to create VPC, Subnets, NAT, and Routing.


## ⚙️ **Configuration**
Before running Pulumi, set your configuration values:

```bash
pulumi config set aws:region ap-southeast-1
pulumi config set vpcCidr 10.0.0.0/16
pulumi config set publicSubnetCidr 10.0.1.0/24
pulumi config set privateSubnetCidr 10.0.2.0/24
pulumi config set instanceType t2.micro
pulumi config set --secret DB_PASSWORD <your-strong-password>


## 🛠️ **Verify Setup**

## Check stack preview:
```bash pulumi preview

## Check stack preview:
```bash pulumi preview

## Deploy resources:
```bash pulumi up

## Test MySQL connectivity from Bastion:
```bash mysql -h <private-instance-ip> -u appuser -p

## Test MySQL connectivity from Bastion:
```bash pulumi destroy
``bash pulumi stack rm


