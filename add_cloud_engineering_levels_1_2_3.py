"""
Add Cloud Engineering Quizzes - Levels 1, 2, and 3
This script adds 60 questions for Cloud Engineering specialization
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_cloud_engineering_quizzes():
    db = SessionLocal()
    try:
        # Get Cloud Engineering specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Cloud Engineering"
        ).first()
        
        if not specialization:
            print("Error: Cloud Engineering specialization not found")
            print("Checking available specializations...")
            all_specs = db.query(models.Specialization).all()
            for spec in all_specs:
                if "cloud" in spec.name.lower():
                    print(f"  Found: {spec.name} (ID: {spec.id})")
            return
        
        print(f"Found specialization: {specialization.name} (ID: {specialization.id})")
        
        # Delete existing quizzes for levels 1, 2, and 3
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == specialization.id,
            models.Quiz.difficulty_level.in_([1, 2, 3])
        ).all()
        
        for quiz in existing_quizzes:
            # Delete quiz attempts first
            db.query(models.QuizAttempt).filter(
                models.QuizAttempt.quiz_id == quiz.id
            ).delete()
            
            # Delete question options
            for question in quiz.questions:
                db.query(models.QuestionOption).filter(
                    models.QuestionOption.question_id == question.id
                ).delete()
            
            # Delete questions
            db.query(models.Question).filter(
                models.Question.quiz_id == quiz.id
            ).delete()
            
            # Delete quiz
            db.query(models.Quiz).filter(models.Quiz.id == quiz.id).delete()
        
        db.commit()
        print(f"Deleted {len(existing_quizzes)} existing quizzes for levels 1-3")
        
        # Level 1: Basic Foundations (20 questions)
        level_1_questions = [
            ('What is "cloud computing"?',
             ["A service that stores all data on a single, local hard drive.",
              "A network of physical servers located in a private home or office.",
              "The on-demand delivery of IT resources (e.g., servers, storage) over the internet.",
              "A type of software used exclusively for advanced data analysis.",
              "A programming framework for building desktop applications."],
             2, "Cloud computing delivers IT resources on-demand over the internet, enabling scalability and flexibility."),
            
            ('What does "IaaS" stand for?',
             ["Internet as a Service",
              "Infrastructure as a Service",
              "Integration as a Service",
              "Information as a Service",
              "Identity as a Service"],
             1, "IaaS (Infrastructure as a Service) provides virtualized computing resources over the internet."),
            
            ('Which option is an example of "SaaS" (Software as a Service)?',
             ["A service providing raw virtual machines for you to manage.",
              "A service providing a platform to build and deploy your own apps.",
              "A fully managed application delivered over the web, like Gmail or Salesforce.",
              "A type of secure network connection to a data center.",
              "A local database installed on your personal computer."],
             2, "SaaS delivers fully managed applications over the web (e.g., Gmail, Salesforce, Office 365)."),
            
            ('What is "PaaS" (Platform as a Service)?',
             ["A service providing raw virtual machines and configurable networking.",
              "A managed platform (e.g., database, OS) to build and deploy apps.",
              "A fully managed application like a word processor or email.",
              "A physical server that you purchase and keep in an office.",
              "A type of security software that scans for viruses."],
             1, "PaaS provides a managed platform (OS, runtime, database) for building and deploying applications."),
            
            ("Which of these is a major cloud provider?",
             ["Linux",
              "Intel",
              "Oracle",
              "Python",
              "Amazon Web Services (AWS)"],
             4, "AWS is one of the major cloud providers, along with Microsoft Azure and Google Cloud Platform."),
            
            ('What is a "virtual machine" (VM)?',
             ["A physical, high-performance server.",
              "A software-based emulation of a physical computer.",
              "A type of network firewall.",
              "A storage device for backups.",
              "A tool for writing application code."],
             1, "A VM is a software emulation of a physical computer, running on shared hardware."),
            
            ('What is a "Region" in a cloud context?',
             ["A specific, physical data center.",
              "A geographic area in the world (e.g., \"US East\") containing data centers.",
              "A user's local neighborhood.",
              "A section of a hard drive used for storage.",
              "A group of users with the same permissions."],
             1, "A Region is a geographic area containing multiple data centers (Availability Zones)."),
            
            ('What is an "Availability Zone" (AZ)?',
             ["A single, isolated data center (or group of data centers) within a Region.",
              "The entire geographical area, such as \"North America\".",
              "A setting that determines if a service is available.",
              "A type of network connection.",
              "A specific virtual machine."],
             0, "An AZ is an isolated data center within a Region, providing fault tolerance."),
            
            ('What is "object storage" (e.g., AWS S3, Azure Blob)?',
             ["A service for storing data in a relational database.",
              "A service for storing files and data as \"objects\" in a flat structure.",
              "A service for running application code.",
              "A service for managing user identities.",
              "A physical hard drive attached to a server."],
             1, "Object storage stores data as objects with metadata in a flat, scalable structure."),
            
            ('What is "block storage" (e.g., AWS EBS, Azure Disk)?',
             ["A virtual hard drive that attaches to a single VM, used for its OS and files.",
              "A service for storing files that can be accessed from the internet.",
              "A service for managing user passwords.",
              "A database for storing data in blocks.",
              "A type of network firewall."],
             0, "Block storage provides virtual hard drives that attach to VMs for OS and application storage."),
            
            ('What is a "public cloud"?',
             ["A cloud environment built and operated by a company for its own private use.",
              "A cloud environment where IT resources are owned and operated by a third-party provider and delivered over the internet.",
              "A mix of both public and private cloud environments.",
              "A cloud that is not secure and is open to the public.",
              "A small-scale cloud built in a local office."],
             1, "Public clouds are owned by third-party providers (AWS, Azure, GCP) and accessible over the internet."),
            
            ('What is a "private cloud"?',
             ["A cloud environment built and operated by a single company for its own use.",
              "A cloud environment that is open to the public for anyone to use.",
              "A mix of public and on-premises environments.",
              "A small, personal laptop.",
              "A cloud provider like AWS or Google Cloud."],
             0, "Private clouds are dedicated infrastructure operated by a single organization."),
            
            ('What is a "hybrid cloud"?',
             ["A cloud environment that only uses virtual machines.",
              "A cloud environment that only uses SaaS products.",
              "An architecture that combines a private cloud with one or more public clouds.",
              "A cloud provider that has not been fully launched.",
              "A cloud that is powered by hybrid (gas and electric) generators."],
             2, "Hybrid clouds integrate private cloud infrastructure with public cloud services."),
            
            ('What does "scalability" mean in the cloud?',
             ["The ability to increase or decrease IT resources (e.g., servers) as needed.",
              "The ability to access resources from anywhere in the world.",
              "The ability to secure data using encryption.",
              "The ability to run code.",
              "The ability to create user accounts."],
             0, "Scalability is the ability to adjust resources up or down based on demand."),
            
            ('What is "elasticity" in a cloud context?',
             ["The physical flexibility of the server hardware.",
              "The ability of the cloud to automatically scale resources up and down.",
              "The process of stretching a network cable.",
              "A type of subscription model for cloud services.",
              "A security feature for data."],
             1, "Elasticity enables automatic, dynamic scaling of resources based on demand."),
            
            ('What is the "pay-as-you-go" pricing model?',
             ["A model where you pay a large, fixed fee once per year.",
              "A model where you only pay for the specific IT resources you consume.",
              "A model where you pay for resources, but only if your application is successful.",
              "A free model where you do not have to pay.",
              "A model where you must pay for all resources in a region."],
             1, "Pay-as-you-go means you only pay for the resources you actually use."),
            
            ('What is a "VPC" (Virtual Private Cloud)?',
             ["A physical, private network in your office.",
              "A logically isolated section of the public cloud, creating a private network.",
              "A type of virtual machine.",
              "A storage device for files.",
              "A user's personal computer."],
             1, "A VPC is a logically isolated virtual network within the public cloud."),
            
            ('What is "Azure"?',
             ["The cloud computing platform from Google.",
              "The cloud computing platform from Microsoft.",
              "The cloud computing platform from Amazon.",
              "A type of open-source database.",
              "A programming language for cloud."],
             1, "Azure is Microsoft's cloud computing platform."),
            
            ('What is "GCP"?',
             ["The cloud computing platform from Google.",
              "The cloud computing platform from Microsoft.",
              "The cloud computing platform from Amazon.",
              "A type of security protocol.",
              "A hardware manufacturer."],
             0, "GCP (Google Cloud Platform) is Google's cloud computing platform."),
            
            ('What is "IAM" (Identity and Access Management)?',
             ["A service for managing users, groups, and permissions.",
              "A service for monitoring application performance.",
              "A service for creating virtual machines.",
              "A service for storing files and objects.",
              "A service for creating virtual networks."],
             0, "IAM manages user identities, authentication, and authorization for cloud resources."),
        ]
        
        quiz_1 = models.Quiz(
            title="Cloud Engineering - Basic Foundations",
            description="Cloud fundamentals: IaaS/PaaS/SaaS, major providers (AWS/Azure/GCP), VMs, Regions, AZs, storage types, and IAM basics",
            specialization_id=specialization.id,
            difficulty_level=1,
            time_limit_minutes=25
        )
        db.add(quiz_1)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_1_questions):
            question = models.Question(
                quiz_id=quiz_1.id,
                question_text=question_text,
                question_type='multiple_choice',
                explanation=explanation,
                order_index=idx
            )
            db.add(question)
            db.flush()
            
            for opt_idx, option_text in enumerate(options):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(opt_idx == correct_idx),
                    order_index=opt_idx
                )
                db.add(option)
        
        print(f"Added Level 1 (Basic Foundations): {len(level_1_questions)} questions")
        
        # Level 2: Intermediate Application (20 questions)
        level_2_questions = [
            ("What is the AWS service for running virtual machines?",
             ["S3 (Simple Storage Service)",
              "RDS (Relational Database Service)",
              "EC2 (Elastic Compute Cloud)",
              "VPC (Virtual Private Cloud)",
              "Lambda"],
             2, "EC2 (Elastic Compute Cloud) is AWS's service for running virtual machines."),
            
            ("What is the Azure equivalent of AWS EC2?",
             ["Azure Blob Storage",
              "Azure SQL Database",
              "Azure Virtual Network",
              "Azure Virtual Machines",
              "Azure Functions"],
             3, "Azure Virtual Machines is the equivalent of AWS EC2 for running VMs."),
            
            ('What is an "AMI" (Amazon Machine Image)?',
             ["A type of virtual network configuration.",
              "A template containing the software (OS, apps) to create a VM.",
              "A managed database service instance.",
              "A storage device used for backups.",
              "A user's security credential file."],
             1, "An AMI is a template with the OS and software configuration for launching EC2 instances."),
            
            ('What is a "Security Group" in AWS?',
             ["A group of users who all have the same security clearance.",
              "A virtual firewall at the instance level that controls inbound/outbound traffic.",
              "A physical security device in a data center.",
              "A type of IAM policy.",
              "A tool for scanning for viruses."],
             1, "Security Groups are virtual firewalls controlling traffic to/from EC2 instances."),
            
            ('What is the Azure equivalent of an AWS "Security Group"?',
             ["A \"Resource Group\"",
              "An \"Availability Set\"",
              "A \"Network Security Group\" (NSG)",
              "A \"Virtual Network\" (VNet)",
              "An \"Azure Policy\""],
             2, "Network Security Groups (NSGs) are Azure's equivalent to AWS Security Groups."),
            
            ('What is a "subnet" in a VPC?',
             ["A sub-section of a larger network (VPC), often used to isolate resources.",
              "A type of storage device.",
              "A template for creating a virtual machine.",
              "A group of users.",
              "A container for storing files."],
             0, "Subnets are subdivisions of a VPC used to organize and isolate resources."),
            
            ('What is an "IAM Role"?',
             ["A set of permissions that you attach to a user or group.",
              "An identity with permissions that a service (like an EC2 instance) can assume.",
              "A password policy for an account.",
              "A type of virtual machine.",
              "A physical security key."],
             1, "IAM Roles provide temporary credentials for services to access other resources."),
            
            ('What is the "CLI"?',
             ["\"Cloud Login Interface,\" a graphical tool for logging in.",
              "\"Command Line Interface,\" a text-based tool for interacting with cloud services.",
              "\"Cloud Logic Inspector,\" a tool for debugging code.",
              "\"Client License Information,\" a file for software activation.",
              "\"Container Launch Initiative,\" a tool for Docker."],
             1, "CLI (Command Line Interface) is a text-based tool for managing cloud resources."),
            
            ('What is an "SDK" (Software Development Kit)?',
             ["A set of libraries that let you interact with cloud services from your code.",
              "A virtual server for development.",
              "A security key for accessing an account.",
              "A text-based command-line tool.",
              "A pre-built virtual machine image."],
             0, "SDKs provide libraries for programmatically interacting with cloud services."),
            
            ('What is a "load balancer"?',
             ["A service that distributes incoming network traffic across multiple servers.",
              "A service that \"balances\" the cost of your servers.",
              "A service that \"balances\" the storage on your hard drives.",
              "A security tool that blocks all traffic.",
              "A database for managing user loads."],
             0, "Load balancers distribute traffic across multiple servers for availability and performance."),
            
            ('What is "AWS S3" used for?',
             ["Running virtual machines.",
              "Storing files (objects) in a highly scalable way.",
              "Managing relational databases.",
              "Creating private networks.",
              "Running serverless code."],
             1, "S3 (Simple Storage Service) is AWS's object storage service for files and data."),
            
            ('What is "AWS RDS"?',
             ["A service for running virtual machines.",
              "A service for storing files as objects.",
              "A managed service for running relational databases (e.g., MySQL, Postgres).",
              "A service for managing user permissions.",
              "A service for monitoring application logs."],
             2, "RDS (Relational Database Service) is AWS's managed database service."),
            
            ('What is the primary difference between an "IAM User" and an "IAM Role"?',
             ["A User is for a person; a Role is for a service. Both provide permissions.",
              "A User has a password; a Role does not.",
              "A User is permanent; a Role is temporary.",
              "A User has more permissions than a Role.",
              "A User is for AWS; a Role is for Azure."],
             0, "Users represent people with credentials; Roles are assumed by services for temporary access."),
            
            ('What is a "snapshot"?',
             ["A point-in-time backup of a block storage volume (like an EBS volume).",
              "A screenshot of your virtual machine's desktop.",
              "A copy of a file from an S3 bucket.",
              "A type of security scan.",
              "A log file from a server."],
             0, "Snapshots are point-in-time backups of block storage volumes."),
            
            ('What is a "public subnet"?',
             ["A subnet that is accessible to all users within your organization.",
              "A subnet whose traffic is routed to an \"Internet Gateway,\" making it reachable from the internet.",
              "A subnet that is not secure and should not be used.",
              "A subnet that contains only storage devices.",
              "A subnet that is shared between multiple AWS accounts."],
             1, "Public subnets have routes to an Internet Gateway, allowing internet access."),
            
            ('What is a "private subnet"?',
             ["A subnet that cannot access any other services.",
              "A subnet that is not directly reachable from the public internet.",
              "A subnet that is encrypted.",
              "A subnet that is more expensive.",
              "A subnet that can only be used by one person."],
             1, "Private subnets lack direct internet access and are isolated from public traffic."),
            
            ('What is a "key pair" used for when launching an AWS EC2 instance?',
             ["To encrypt the instance's hard drive.",
              "To authenticate (log in) to a Linux instance via SSH.",
              "To define the username and password for the instance.",
              "To unlock the instance from a \"locked\" state.",
              "To provide the \"key\" and \"value\" for a tag."],
             1, "Key pairs provide SSH authentication for accessing Linux EC2 instances."),
            
            ("What is the GCP service for object storage?",
             ["Google Kubernetes Engine",
              "Google Compute Engine",
              "Google Cloud Storage",
              "Google Cloud SQL",
              "Google BigQuery"],
             2, "Google Cloud Storage is GCP's object storage service."),
            
            ("What is the GCP service for running virtual machines?",
             ["Google Kubernetes Engine",
              "Google Compute Engine",
              "Google Cloud Storage",
              "Google Cloud SQL",
              "Google App Engine"],
             1, "Google Compute Engine is GCP's service for running virtual machines."),
            
            ('What is an "S3 Bucket"?',
             ["A container (folder) for storing objects (files) in AWS S3.",
              "A physical hard drive used for S3.",
              "A type of virtual machine.",
              "A security policy for S3.",
              "A user account for S3."],
             0, "S3 Buckets are containers for organizing and storing objects in S3."),
        ]
        
        quiz_2 = models.Quiz(
            title="Cloud Engineering - Intermediate Application",
            description="Cloud services: EC2/VMs, AMI, Security Groups, subnets, IAM roles, CLI/SDK, load balancers, S3, RDS, and key pairs",
            specialization_id=specialization.id,
            difficulty_level=2,
            time_limit_minutes=30
        )
        db.add(quiz_2)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_2_questions):
            question = models.Question(
                quiz_id=quiz_2.id,
                question_text=question_text,
                question_type='multiple_choice',
                explanation=explanation,
                order_index=idx
            )
            db.add(question)
            db.flush()
            
            for opt_idx, option_text in enumerate(options):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(opt_idx == correct_idx),
                    order_index=opt_idx
                )
                db.add(option)
        
        print(f"Added Level 2 (Intermediate Application): {len(level_2_questions)} questions")
        
        # Level 3: Advanced Scenarios (20 questions)
        level_3_questions = [
            ('What is an "Auto Scaling Group"?',
             ["A tool that automatically encrypts all data on a virtual machine.",
              "A service that automatically adjusts the number of VMs based on traffic or a schedule.",
              "A service that automatically backs up a database.",
              "A tool that automatically assigns IP addresses to new VMs.",
              "A service that automatically patches the operating system."],
             1, "Auto Scaling Groups automatically adjust VM capacity based on demand or schedules."),
            
            ('What is a "NAT Gateway"?',
             ["A service that allows instances in a private subnet to initiate outbound traffic to the internet.",
              "A service that allows inbound traffic from the internet to a private subnet.",
              "A service that translates domain names into IP addresses.",
              "A type of load balancer.",
              "A security service that blocks all internet traffic."],
             0, "NAT Gateways enable private subnet instances to access the internet for outbound traffic."),
            
            ('What is a "read replica" for a database?',
             ["A read-only copy of a database, used to offload read queries and improve performance.",
              "A full backup of a database.",
              "A security tool that \"reads\" database logs for threats.",
              "A type of database that can only be read, not written to.",
              "A user who only has read-only permissions."],
             0, "Read replicas are read-only database copies that improve read performance."),
            
            ('What is "Multi-AZ" for a database (e.g., AWS RDS)?',
             ["A feature that creates a standby replica in a different Availability Zone for high availability.",
              "A feature that creates multiple read replicas in different regions.",
              "A feature that allows a database to be accessed from multiple zones.",
              "A security feature that encrypts the database in multiple zones.",
              "A feature that scales the database across multiple zones."],
             0, "Multi-AZ creates synchronous standby replicas in different AZs for high availability."),
            
            ('What is the difference between an "Application Load Balancer" (ALB) and a "Network Load Balancer" (NLB)?',
             ["ALB operates at Layer 7 (HTTP); NLB operates at Layer 4 (TCP).",
              "ALB operates at Layer 4 (TCP); NLB operates at Layer 7 (HTTP).",
              "ALB is for internal traffic; NLB is for external traffic.",
              "ALB is less secure than an NLB.",
              "ALB is an older, deprecated service."],
             0, "ALBs operate at Layer 7 (application/HTTP); NLBs operate at Layer 4 (transport/TCP)."),
            
            ('What is "AWS CloudWatch"?',
             ["A service for managing user permissions.",
              "A service for monitoring resources, collecting logs, and setting alarms.",
              "A service for storing files.",
              "A service for creating virtual networks.",
              "A service for building websites."],
             1, "CloudWatch monitors AWS resources, collects metrics and logs, and triggers alarms."),
            
            ('What is "Azure Monitor"?',
             ["A service for managing virtual machines.",
              "A service for monitoring resources, collecting logs, and setting alerts.",
              "A service for managing databases.",
              "A service for user authentication.",
              "A service for storing files."],
             1, "Azure Monitor provides comprehensive monitoring, logging, and alerting for Azure resources."),
            
            ('What is an "S3 Lifecycle Policy"?',
             ["A policy that automatically moves objects to cheaper storage tiers or deletes them after a set time.",
              "A security policy that defines who can access an S3 bucket.",
              "A policy that defines the maximum size of an S3 bucket.",
              "A backup policy for S3.",
              "A policy that tracks the \"life\" of an S3 bucket."],
             0, "Lifecycle policies automate object transitions to cheaper storage or deletion based on age."),
            
            ('What does an "IAM Policy" do?',
             ["It defines a user's password requirements.",
              "It defines the permissions (e.g., \"Allow S3:GetObject\") for a user, group, or role.",
              "It creates a new IAM user.",
              "It monitors a user's activity.",
              "It is a physical security policy."],
             1, "IAM Policies define permissions (allow/deny actions) for users, groups, and roles."),
            
            ('What is "AWS Route 53"?',
             ["A scalable Domain Name System (DNS) web service.",
              "A service for creating private networks.",
              "A service for monitoring network traffic.",
              "A security service for blocking attacks.",
              "A service for creating virtual machines."],
             0, "Route 53 is AWS's scalable DNS service for domain name resolution."),
            
            ('What is "Azure DNS"?',
             ["A managed service for running relational databases.",
              "A hosting service for DNS domains, providing name resolution.",
              "A service for managing virtual networks.",
              "A security service for monitoring traffic.",
              "A service for creating virtual machines."],
             1, "Azure DNS hosts and manages DNS domains for name resolution."),
            
            ('What is a "VPC Peering" connection?',
             ["A connection that links a VPC to the public internet.",
              "A connection that links a VPC to an on-premises data center.",
              "A private network connection between two separate VPCs.",
              "A connection that links a user's laptop to a VPC.",
              "A connection that links a VM to a storage bucket."],
             2, "VPC Peering creates private network connections between two VPCs."),
            
            ('What is a "security best practice" for an AWS account?',
             ["Use the \"root\" user for all daily tasks.",
              "Enable Multi-Factor Authentication (MFA) on the \"root\" user.",
              "Store access keys directly in your application code.",
              "Open all ports on your security groups.",
              "Never update your IAM policies."],
             1, "Best practice: Enable MFA on root user and avoid using root for daily operations."),
            
            ('What is a "Resource Group" in Azure?',
             ["A logical container that holds related Azure resources (e.g., VMs, storage, VNets).",
              "A group of users with the same permissions.",
              "A set of security rules.",
              "A specific data center location.",
              "A type of virtual machine."],
             0, "Resource Groups are logical containers for organizing related Azure resources."),
            
            ('What is the difference between "AWS EBS" and "AWS S3"?',
             ["EBS is object storage; S3 is block storage.",
              "EBS is block storage (a VM hard drive); S3 is object storage (for files).",
              "EBS is a database; S3 is a virtual machine.",
              "EBS is free; S3 is expensive.",
              "There is no difference; they are the same service."],
             1, "EBS provides block storage for VMs; S3 provides object storage for files and data."),
            
            ('What is a "CDN" (Content Delivery Network) like AWS CloudFront?',
             ["A service that \"caches\" content (e.g., images, videos) in locations closer to users.",
              "A service for creating virtual networks.",
              "A service for managing databases.",
              "A service for monitoring security.",
              "A service for running application code."],
             0, "CDNs cache content at edge locations globally to reduce latency for users."),
            
            ('What is an "API Gateway"?',
             ["A managed service that acts as a \"front door\" for APIs to handle traffic, security, and monitoring.",
              "A physical hardware device for network routing.",
              "A security service that only blocks traffic.",
              "A tool for writing application code.",
              "A database for storing API keys."],
             0, "API Gateways manage API traffic, handle authentication, throttling, and monitoring."),
            
            ('What is the "Shared Responsibility Model"?',
             ["The idea that you and the cloud provider share the cost of all services.",
              "The idea that the cloud provider is fully responsible for all security.",
              "The idea that you are fully responsible for all security.",
              "The idea that the provider is responsible for security of the cloud, and you are responsible for security in the cloud.",
              "A legal document that transfers all responsibility to you."],
             3, "Provider secures infrastructure (of the cloud); customers secure their data/apps (in the cloud)."),
            
            ('What is "AWS CloudFormation"?',
             ["A service for monitoring application performance.",
              "An \"Infrastructure as Code\" (IaC) service for provisioning AWS resources with templates.",
              "A service for storing and managing files.",
              "A managed database service.",
              "A tool for designing application architecture."],
             1, "CloudFormation provisions AWS infrastructure using declarative JSON/YAML templates."),
            
            ('What is "Azure Resource Manager" (ARM)?',
             ["The underlying \"Infrastructure as Code\" (IaC) service for provisioning Azure resources.",
              "A tool for managing employee access to resources.",
              "A monitoring and logging service.",
              "A physical manager for Azure data centers.",
              "A service for building virtual machines."],
             0, "ARM is Azure's IaC service for deploying and managing resources via templates."),
        ]
        
        quiz_3 = models.Quiz(
            title="Cloud Engineering - Advanced Scenarios",
            description="Advanced cloud: Auto Scaling, NAT Gateway, read replicas, Multi-AZ, load balancers, monitoring, lifecycle policies, VPC peering, IaC, and CDN",
            specialization_id=specialization.id,
            difficulty_level=3,
            time_limit_minutes=35
        )
        db.add(quiz_3)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_3_questions):
            question = models.Question(
                quiz_id=quiz_3.id,
                question_text=question_text,
                question_type='multiple_choice',
                explanation=explanation,
                order_index=idx
            )
            db.add(question)
            db.flush()
            
            for opt_idx, option_text in enumerate(options):
                option = models.QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    is_correct=(opt_idx == correct_idx),
                    order_index=opt_idx
                )
                db.add(option)
        
        print(f"Added Level 3 (Advanced Scenarios): {len(level_3_questions)} questions")
        
        db.commit()
        print("\n✅ Successfully added Cloud Engineering quizzes (Levels 1-3 complete!)")
        print(f"Total questions added: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_cloud_engineering_quizzes()
