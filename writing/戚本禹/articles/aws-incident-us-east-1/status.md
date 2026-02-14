# AWS Incident - Oct 20, 2024 - US-EAST-1

**Source**: https://health.aws.amazon.com/health/status

**Summary**: Operational issue - Multiple services (N. Virginia)
**Severity**: Impacted (95 services)
**Duration**: Oct 20, 12:11 AM PDT - 1:03 PM PDT (approx 13 hours)

---

## Timeline

### Oct 20 1:03 PM PDT
Service recovery across all AWS services continues to improve. We continue to reduce throttles for new EC2 Instance launches in the US-EAST-1 Region that were put in place to help mitigate impact. Lambda invocation errors have fully recovered and function errors continue to improve. We have scaled up the rate of polling SQS queues via Lambda Event Source Mappings to pre-event levels. We will provide another update by 1:45 PM PDT.

### Oct 20 12:15 PM PDT
We continue to observe recovery across all AWS services, and instance launches are succeeding across multiple Availability Zones in the US-EAST-1 Regions. For Lambda, customers may face intermittent function errors for functions making network requests to other services or systems as we work to address residual network connectivity issues. To recover Lambda's invocation errors, we slowed down the rate of SQS polling via Lambda Event Source Mappings. We are now increasing the rate of SQS polling as we experience more successful invocations and reduced function errors. We will provide another update by 1:00 PM PDT.

### Oct 20 11:22 AM PDT
Our mitigations to resolve launch failures for new EC2 instances continue to progress and we are seeing increased launches of new EC2 instances and decreasing networking connectivity issues in the US-EAST-1 Region. We are also experiencing significant improvements to Lambda invocation errors, especially when creating new execution environments (including for Lambda@Edge invocations). We will provide an update by 12:00 PM PDT.

### Oct 20 10:38 AM PDT
Our mitigations to resolve launch failures for new EC2 instances are progressing and the internal subsystems of EC2 are now showing early signs of recovering in a few Availability Zones (AZs) in the US-EAST-1 Region. We are applying mitigations to the remaining AZs at which point we expect launch errors and network connectivity issues to subside. We will provide an update by 11:30 AM PDT.

### Oct 20 10:03 AM PDT
We continue to apply mitigation steps for network load balancer health and recovering connectivity for most AWS services. Lambda is experiencing function invocation errors because an internal subsystem was impacted by the network load balancer health checks. We are taking steps to recover this internal Lambda system. For EC2 launch instance failures, we are in the process of validating a fix and will deploy to the first AZ as soon as we have confidence we can do so safely. We will provide an update by 10:45 AM PDT.

### Oct 20 9:13 AM PDT
We have taken additional mitigation steps to aid the recovery of the underlying internal subsystem responsible for monitoring the health of our network load balancers and are now seeing connectivity and API recovery for AWS services. We have also identified and are applying next steps to mitigate throttling of new EC2 instance launches. We will provide an update by 10:00 AM PDT.

### Oct 20 8:43 AM PDT
**ROOT CAUSE IDENTIFIED**: We have narrowed down the source of the network connectivity issues that impacted AWS Services. The root cause is an underlying internal subsystem responsible for monitoring the health of our network load balancers. We are throttling requests for new EC2 instance launches to aid recovery and actively working on mitigations.

### Oct 20 8:04 AM PDT
We continue to investigate the root cause for the network connectivity issues that are impacting AWS services such as DynamoDB, SQS, and Amazon Connect in the US-EAST-1 Region. We have identified that the issue originated from within the EC2 internal network. We continue to investigate and identify mitigations.

### Oct 20 7:29 AM PDT
We have confirmed multiple AWS services experienced network connectivity issues in the US-EAST-1 Region. We are seeing early signs of recovery for the connectivity issues and are continuing to investigate the root cause.

### Oct 20 7:14 AM PDT
We can confirm significant API errors and connectivity issues across multiple services in the US-EAST-1 Region. We are investigating and will provide further update in 30 minutes or soon if we have additional information.

### Oct 20 6:42 AM PDT
We have applied multiple mitigations across multiple Availability Zones (AZs) in US-EAST-1 and are still experiencing elevated errors for new EC2 instance launches. We are rate limiting new instance launches to aid recovery. We will provide an update at 7:30 AM PDT or sooner if we have additional information.

### Oct 20 5:48 AM PDT
We are making progress on resolving the issue with new EC2 instance launches in the US-EAST-1 Region and are now able to successfully launch new instances in some Availability Zones. We are applying similar mitigations to the remaining impacted Availability Zones to restore new instance launches. As we continue to make progress, customers will see an increasing number of successful new EC2 launches. We continue to recommend that customers launch new EC2 Instance launches that are not targeted to a specific Availability Zone (AZ) so that EC2 has flexibility in selecting the appropriate AZ.

We also wanted to share that we are continuing to successfully process the backlog of events for both EventBridge and Cloudtrail. New events published to these services are being delivered normally and are not experiencing elevated delivery latencies.

We will provide an update by 6:30 AM PDT or sooner if we have additional information to share.

### Oct 20 5:10 AM PDT
We confirm that we have now recovered processing of SQS queues via Lambda Event Source Mappings. We are now working through processing the backlog of SQS messages in Lambda queues.

### Oct 20 4:48 AM PDT
We continue to work to fully restore new EC2 launches in US-EAST-1. We recommend EC2 Instance launches that are not targeted to a specific Availability Zone (AZ) so that EC2 has flexibility in selecting the appropriate AZ. The impairment in new EC2 launches also affects services such as RDS, ECS, and Glue. We also recommend that Auto Scaling Groups are configured to use multiple AZs so that Auto Scaling can manage EC2 instance launches automatically.

We are pursuing further mitigation steps to recover Lambda's polling delays for Event Source Mappings for SQS. AWS features that depend on Lambda's SQS polling capabilities such as Organization policy updates are also experiencing elevated processing times. We will provide an update by 5:30 AM PDT.

### Oct 20 4:08 AM PDT
We are continuing to work towards full recovery for EC2 launch errors, which may manifest as an Insufficient Capacity Error. Additionally, we continue to work toward mitigation for elevated polling delays for Lambda, specifically for Lambda Event Source Mappings for SQS. We will provide an update by 5:00 AM PDT.

### Oct 20 3:35 AM PDT
The underlying DNS issue has been fully mitigated, and most AWS Service operations are succeeding normally now. Some requests may be throttled while we work toward full resolution. Additionally, some services are continuing to work through a backlog of events such as Cloudtrail and Lambda. While most operations are recovered, requests to launch new EC2 instances (or services that launch EC2 instances such as ECS) in the US-EAST-1 Region are still experiencing increased error rates. We continue to work toward full resolution. If you are still experiencing an issue resolving the DynamoDB service endpoints in US-EAST-1, we recommend flushing your DNS caches. We will provide an update by 4:15 AM, or sooner if we have additional information to share.

### Oct 20 3:03 AM PDT
We continue to observe recovery across most of the affected AWS Services. We can confirm global services and features that rely on US-EAST-1 have also recovered. We continue to work towards full resolution and will provide updates as we have more information to share.

### Oct 20 2:27 AM PDT
We are seeing significant signs of recovery. Most requests should now be succeeding. We continue to work through a backlog of queued requests. We will continue to provide additional information.

### Oct 20 2:22 AM PDT
We have applied initial mitigations and we are observing early signs of recovery for some impacted AWS Services. During this time, requests may continue to fail as we work toward full resolution. We recommend customers retry failed requests. While requests begin succeeding, there may be additional latency and some services will have a backlog of work to work through, which may take additional time to fully process. We will continue to provide updates as we have more information to share, or by 3:15 AM.

### Oct 20 2:01 AM PDT
**POTENTIAL ROOT CAUSE**: We have identified a potential root cause for error rates for the DynamoDB APIs in the US-EAST-1 Region. Based on our investigation, the issue appears to be related to DNS resolution of the DynamoDB API endpoint in US-EAST-1. We are working on multiple parallel paths to accelerate recovery. This issue also affects other AWS Services in the US-EAST-1 Region. Global services or features that rely on US-EAST-1 endpoints such as IAM updates and DynamoDB Global tables may also be experiencing issues. During this time, customers may be unable to create or update Support Cases. We recommend customers continue to retry any failed requests. We will continue to provide updates as we have more information to share, or by 2:45 AM.

### Oct 20 1:26 AM PDT
We can confirm significant error rates for requests made to the DynamoDB endpoint in the US-EAST-1 Region. This issue also affects other AWS Services in the US-EAST-1 Region as well. During this time, customers may be unable to create or update Support Cases. Engineers were immediately engaged and are actively working on both mitigating the issue, and fully understanding the root cause. We will continue to provide updates as we have more information to share, or by 2:00 AM.

### Oct 20 12:51 AM PDT
We can confirm increased error rates and latencies for multiple AWS Services in the US-EAST-1 Region. This issue may also be affecting Case Creation through the AWS Support Center or the Support API. We are actively engaged and working to both mitigate the issue and understand root cause. We will provide an update in 45 minutes, or sooner if we have additional information to share.

### Oct 20 12:11 AM PDT (INCIDENT START)
We are investigating increased error rates and latencies for multiple AWS services in the US-EAST-1 Region. We will provide another update in the next 30-45 minutes.

---

## Explicitly Mentioned Affected Services

From the status updates, the following services were explicitly mentioned as affected:

1. EC2 (and EC2 instance launches)
2. DynamoDB
3. SQS
4. Amazon Connect
5. Lambda (including Lambda@Edge)
6. EventBridge
7. CloudTrail
8. RDS
9. ECS
10. Glue
11. Auto Scaling
12. IAM (global service)
13. DynamoDB Global Tables (global feature)
14. Support Center/Support API
15. Organization policy updates
16. Network Load Balancer (internal health checks)
17. DNS (internal subsystem)

---

## Root Causes Identified

1. **DNS resolution issue** for DynamoDB API endpoint in US-EAST-1 (identified at 2:01 AM PDT)
2. **Network load balancer health monitoring subsystem** failure (identified at 8:43 AM PDT)
3. Issue originated from within **EC2 internal network** (8:04 AM PDT)

---

## Key Observations

1. **Cascading failures**: EC2 failures → RDS, ECS, Glue failures
2. **Global service impact**: US-EAST-1 issues affected global services (IAM, DynamoDB Global Tables)
3. **Service interdependencies**: Lambda depends on internal subsystems affected by NLB health checks
4. **Recovery challenges**: Backlog processing for EventBridge, CloudTrail, SQS took hours after initial recovery
5. **Mitigation trade-offs**: Throttling EC2 launches to aid recovery, slowing SQS polling to recover Lambda

---

## AWS's Mitigation Strategies

1. Throttling new EC2 instance launches
2. Rate limiting instance launches to specific AZs
3. Slowing down SQS polling via Lambda Event Source Mappings
4. Recommending multi-AZ deployments
5. Recommending DNS cache flushing
6. Parallel mitigation paths
