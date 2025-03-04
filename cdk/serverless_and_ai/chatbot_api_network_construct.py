from typing import Final

from aws_cdk import aws_ec2
from constructs import Construct


class ChatBotNetworkConstruct(Construct):
    _VPC_CIDR: Final[str] = '10.1.0.0/16'
    _REDIS_PORT: Final[int] = 6379

    def __init__(self, scope: Construct, stack_id: str) -> None:
        super().__init__(scope, stack_id)
        self._scope = scope
        subnets = [
            aws_ec2.SubnetConfiguration(name="public-subnet-1", subnet_type=aws_ec2.SubnetType.PUBLIC, cidr_mask=24),
            aws_ec2.SubnetConfiguration(name="private-subnet-1", subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS, cidr_mask=24)
        ]
        self.vpc = aws_ec2.Vpc(self, "ChatBotVPC", max_azs=2, nat_gateways=1, ip_addresses=aws_ec2.IpAddresses.cidr(self._VPC_CIDR),
                               subnet_configuration=subnets, restrict_default_security_group=True, enable_dns_support=True,
                               enable_dns_hostnames=True)
        self.vpc_sg = aws_ec2.SecurityGroup(self, "ChatBotVPCSecurityGroup", vpc=self.vpc, allow_all_outbound=True)
        self.vpc_sg.connections.allow_from(
            aws_ec2.Peer.ipv4(self._VPC_CIDR), aws_ec2.Port.tcp(self._REDIS_PORT), description='Allow Redis access from witihin VPC CIDR')
