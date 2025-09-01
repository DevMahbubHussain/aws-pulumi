### **AWS Hands-On Exam (Pulumi)**


### Task 1 — Create a Secure VPC

This project uses **Pulumi** with **Python** to create a basic AWS networking setup, including:
- VPC
- Public and Private Subnets
- Internet Gateway (IGW)
- NAT Gateway
- Public and Private Route Tables

Task1:
- `images/task1/pulumi-preview.png`
- `images/task1/pulumi-up.png`
- `images/task1/pulumi-stack.png`
- `images/task1/stackjson.png`

![Alt text](images/task1/pulumi-preview.png)



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





