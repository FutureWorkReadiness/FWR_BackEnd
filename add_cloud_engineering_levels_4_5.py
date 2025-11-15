"""
Add Cloud Engineering Quizzes - Levels 4 and 5
This script adds 40 questions for Cloud Engineering specialization (Expert through Strategic)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_cloud_engineering_advanced_quizzes():
    db = SessionLocal()
    try:
        # Get Cloud Engineering specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Cloud Engineering"
        ).first()
        
        if not specialization:
            print("Error: Cloud Engineering specialization not found")
            return
        
        print(f"Found specialization: {specialization.name} (ID: {specialization.id})")
        
        # Delete existing quizzes for levels 4 and 5
        existing_quizzes = db.query(models.Quiz).filter(
            models.Quiz.specialization_id == specialization.id,
            models.Quiz.difficulty_level.in_([4, 5])
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
        print(f"Deleted {len(existing_quizzes)} existing quizzes for levels 4-5")
        
        # Level 4: Expert & Specialization (20 questions)
        level_4_questions = [
            ('What is "Infrastructure as Code" (IaC)?',
             ["The process of managing and provisioning infrastructure through code (e.g., Terraform, CloudFormation).",
              "A hardware device that writes infrastructure code for you.",
              "The practice of storing all application code inside the server's OS.",
              "A type of networking protocol for cloud.",
              "A monitoring tool that checks your code."],
             0, "IaC manages and provisions infrastructure using code rather than manual processes."),
            
            ('What is "Terraform"?',
             ["An AWS-native service for IaC.",
              "A cloud-agnostic (multi-cloud) \"Infrastructure as Code\" (IaC) tool.",
              "A service for monitoring application performance.",
              "A container orchestration service.",
              "A serverless computing platform."],
             1, "Terraform is a cloud-agnostic IaC tool that works across multiple cloud providers."),
            
            ('What is "Docker"?',
             ["A tool for provisioning and managing virtual machines.",
              "A platform for packaging applications and their dependencies into a \"container.\"",
              "A serverless computing service.",
              "A tool for managing infrastructure as code.",
              "A managed database service."],
             1, "Docker packages applications and dependencies into portable, isolated containers."),
            
            ('What is "Kubernetes" (e.g., EKS, AKS, GKE)?',
             ["A service for automating the deployment, scaling, and management of containerized applications.",
              "A service for building and storing container images.",
              "A service for running single, event-driven functions.",
              "A service for managing virtual networks.",
              "A managed NoSQL database service."],
             0, "Kubernetes orchestrates containerized applications, handling deployment, scaling, and management."),
            
            ('What is "serverless" computing (e.g., AWS Lambda, Azure Functions)?',
             ["A model where the cloud provider manages the servers, and you run code in response to events.",
              "A model where all code runs directly on the user's browser.",
              "A type of container service (like Kubernetes).",
              "A physical server that has no operating system.",
              "An old model of computing using mainframes."],
             0, "Serverless computing runs event-driven code without managing servers or infrastructure."),
            
            ('What is a "CI/CD pipeline"?',
             ["An automated workflow for building, testing, and deploying application code.",
              "A physical \"pipeline\" for network traffic.",
              "A security protocol for data.",
              "A tool for managing databases.",
              "A monitoring and logging service."],
             0, "CI/CD pipelines automate the process of building, testing, and deploying code."),
            
            ('What is "AWS CodePipeline"?',
             ["A managed \"Continuous Integration/Continuous Delivery\" (CI/CD) service.",
              "A code editor that runs in the cloud.",
              "A service for storing and versioning code (like GitHub).",
              "A service for running virtual machines.",
              "A service for monitoring code performance."],
             0, "AWS CodePipeline is a managed CI/CD service for automating release pipelines."),
            
            ('What is "Azure DevOps"?',
             ["A service for managing virtual networks.",
              "A suite of services that includes \"Pipelines\" (CI/CD), \"Repos\" (Git), and \"Boards\" (planning).",
              "A managed database service.",
              "A service for monitoring application logs.",
              "A serverless computing platform."],
             1, "Azure DevOps provides a complete DevOps toolchain: CI/CD, Git repos, planning boards, and more."),
            
            ('What is "AWS Direct Connect" or "Azure ExpressRoute"?',
             ["A dedicated, private network connection from your on-premises data center to the cloud.",
              "A standard internet-based VPN connection.",
              "A type of load balancer.",
              "A service for managing DNS.",
              "A high-speed connection to the public internet."],
             0, "Direct Connect/ExpressRoute provide dedicated private network connections to the cloud."),
            
            ('What is a "Web Application Firewall" (WAF)?',
             ["A firewall that protects a user's web browser.",
              "A firewall that filters Layer 7 (HTTP) traffic to protect web apps from attacks like XSS or SQLi.",
              "A firewall that protects a virtual machine (this is a Security Group / NSG).",
              "A type of antivirus software.",
              "A physical hardware device in a data center."],
             1, "WAFs filter HTTP traffic at Layer 7 to protect web applications from attacks."),
            
            ('What is an "AWS Key Management Service" (KMS) or "Azure Key Vault"?',
             ["A service for securely storing and managing encryption keys and other secrets.",
              "A service for storing and managing SSH key pairs.",
              "A service for storing user passwords.",
              "A hardware security device.",
              "A service for managing API keys."],
             0, "KMS/Key Vault securely store and manage encryption keys and secrets."),
            
            ('What is "AWS DynamoDB"?',
             ["A managed relational (SQL) database service.",
              "A managed NoSQL (key-value and document) database service.",
              "A service for data warehousing.",
              "A service for monitoring database performance.",
              "A service for running virtual machines."],
             1, "DynamoDB is AWS's managed NoSQL database for key-value and document data."),
            
            ('What is "Azure Cosmos DB"?',
             ["A globally distributed, multi-model NoSQL database service.",
              "A managed relational (SQL) database service.",
              "A data warehousing service.",
              "A service for creating virtual networks.",
              "A service for managing user identities."],
             0, "Cosmos DB is Azure's globally distributed, multi-model NoSQL database."),
            
            ('What is the difference between "AWS CloudFormation" and "Terraform"?',
             ["CloudFormation is for AWS; Terraform is for Azure only.",
              "CloudFormation is cloud-agnostic; Terraform is AWS-only.",
              "CloudFormation is AWS-native; Terraform is a cloud-agnostic (multi-cloud) tool.",
              "CloudFormation uses HCL; Terraform uses JSON/YAML.",
              "CloudFormation is for servers; Terraform is for networks."],
             2, "CloudFormation is AWS-specific; Terraform works across multiple cloud providers."),
            
            ('What is a "container registry" (e.g., ECR, ACR)?',
             ["A service for running containers (this is Kubernetes).",
              "A service for storing, managing, and deploying container images.",
              "A tool for building container images.",
              "A security scanner for containers.",
              "A virtual machine optimized for containers."],
             1, "Container registries store, manage, and distribute container images."),
            
            ('What is a "service mesh" (e.g., Istio, Linkerd)?',
             ["A dedicated infrastructure layer for managing service-to-service communication in a microservices architecture.",
              "A physical network mesh in a data center.",
              "A tool for monitoring network traffic.",
              "A type of firewall.",
              "A service for building virtual machines."],
             0, "Service meshes manage communication, security, and observability between microservices."),
            
            ('What is a "VPC Endpoint"?',
             ["A connection that allows you to privately access AWS services without using the public internet.",
              "A public IP address for a VPC.",
              "A VPN connection to a VPC.",
              "A tool for monitoring VPC traffic.",
              "A user's login \"endpoint\" for a VPC."],
             0, "VPC Endpoints enable private access to AWS services without internet traffic."),
            
            ('What is "AWS Shield"?',
             ["A managed \"Distributed Denial of Service\" (DDoS) protection service.",
              "A service for managing encryption keys.",
              "A service for managing user permissions.",
              "A hardware security device.",
              "A Web Application Firewall (WAF)."],
             0, "AWS Shield provides DDoS protection for AWS applications."),
            
            ('What is "Azure Sentinel"?',
             ["A \"Security Information and Event Management\" (SIEM) and \"SOAR\" tool.",
              "A \"Distributed Denial of Service\" (DDoS) protection service.",
              "A service for managing encryption keys.",
              "A Web Application Firewall (WAF).",
              "A service for managing virtual networks."],
             0, "Azure Sentinel is a cloud-native SIEM and SOAR security analytics platform."),
            
            ('What is "AWS EKS"?',
             ["A managed \"Kubernetes\" service.",
              "A managed \"Elasticsearch\" service.",
              "A managed \"Kafka\" service.",
              "A managed \"container registry\" service.",
              "A managed \"serverless\" platform."],
             0, "EKS (Elastic Kubernetes Service) is AWS's managed Kubernetes service."),
        ]
        
        quiz_4 = models.Quiz(
            title="Cloud Engineering - Expert & Specialization",
            description="Expert cloud: IaC, Terraform, Docker, Kubernetes, serverless, CI/CD, WAF, KMS, DynamoDB, Cosmos DB, service mesh, VPC endpoints, Shield, Sentinel",
            specialization_id=specialization.id,
            difficulty_level=4,
            time_limit_minutes=35
        )
        db.add(quiz_4)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_4_questions):
            question = models.Question(
                quiz_id=quiz_4.id,
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
        
        print(f"Added Level 4 (Expert & Specialization): {len(level_4_questions)} questions")
        
        # Level 5: Strategic & Architectural (20 questions)
        level_5_questions = [
            ('What is "High Availability" (HA) in a cloud architecture?',
             ["An architecture designed to be very fast and performant.",
              "An architecture designed to be very low-cost.",
              "An architecture designed to remain operational by eliminating single points of failure (e.g., using multiple AZs).",
              "An architecture that is deployed in a single data center.",
              "An architecture that is managed by a third-party vendor."],
             2, "HA architectures eliminate single points of failure using redundancy across multiple AZs."),
            
            ('How does a "Disaster Recovery" (DR) strategy differ from "High Availability" (HA)?',
             ["HA is about surviving a component failure (e.g., one server); DR is about surviving a site-wide disaster (e.g., an earthquake).",
              "HA is about backups; DR is about live replication.",
              "HA is more expensive than DR and is considered a replacement for it.",
              "HA is for data; DR is for applications.",
              "They are identical strategies with different names."],
             0, "HA handles component failures; DR handles catastrophic site-wide disasters."),
            
            ('What is a "lift-and-shift" (rehosting) cloud migration?',
             ["Re-architecting an application to be fully cloud-native.",
              "Moving an application to the cloud with minimal or no code changes.",
              "Decommissioning an old application and replacing it with a new SaaS product.",
              "Moving an application from one cloud provider to another.",
              "Throwing away the old server (\"lift\") and writing a new one (\"shift\")."],
             1, "Lift-and-shift migrates applications to the cloud with minimal changes (rehosting)."),
            
            ('What is a "re-platform" (lift-and-reshape) cloud migration?',
             ["Moving an application to the cloud with no changes.",
              "Moving an application to the cloud while making minor optimizations (e.g., moving to a managed database).",
              "Fully rewriting the application to be cloud-native.",
              "Decommissioning the application.",
              "Moving the application to a new physical data center."],
             1, "Re-platform makes minor optimizations during migration (e.g., using managed services)."),
            
            ('What is "RPO" (Recovery Point Objective)?',
             ["The maximum amount of data (measured in time) that a business is willing to lose in a disaster (e.g., \"1 hour of data\").",
              "The maximum amount of time it should take to get a system back online after a disaster (e.g., \"4 hours\").",
              "The \"Real Performance Objective\" of a system.",
              "The \"Resource Provisioning Objective\" for a new project.",
              "The \"Role-based Permission Objective\" for a user."],
             0, "RPO is the maximum acceptable data loss measured in time (e.g., last 1 hour)."),
            
            ('What is "RTO" (Recovery Time Objective)?',
             ["The maximum amount of data (measured in time) that a business is willing to lose.",
              "The maximum amount of time it should take to get a system back online after a disaster.",
              "The \"Real Time Objective\" for a system's performance.",
              "The \"Resource Timing Objective\" for a project.",
              "The \"Role-based Time-out Objective\" for a user."],
             1, "RTO is the maximum acceptable downtime for recovery (e.g., 4 hours)."),
            
            ('What is a strategic reason to use "Reserved Instances" (RIs) or "Savings Plans"?',
             ["To gain the ability to automatically scale your instances.",
              "To receive a significant discount in exchange for a 1- or 3-year commitment.",
              "To get instances with more powerful CPUs.",
              "To get instances with better security.",
              "To allow your instances to be moved between regions."],
             1, "RIs/Savings Plans offer significant discounts for 1-3 year commitments."),
            
            ('What is a "Spot Instance"?',
             ["An instance with a fixed, long-term price.",
              "An instance that can be purchased for a very large discount, but can be terminated by the cloud provider at any time.",
              "An instance used specifically for security \"spot checks.\"",
              "An instance that is reserved for your account.",
              "A type of serverless function."],
             1, "Spot Instances offer steep discounts but can be terminated when capacity is needed."),
            
            ('What is a "multi-cloud" strategy?',
             ["The practice of using multiple public clouds (e.g., AWS and Azure) to avoid vendor lock-in.",
              "The practice of using a mix of public and private cloud.",
              "The practice of deploying an application across multiple regions in a single cloud.",
              "The practice of using a CDN.",
              "A strategy that involves multiple layers of cloud security."],
             0, "Multi-cloud uses multiple public cloud providers to avoid vendor lock-in."),
            
            ('What is a "hybrid cloud" strategy?',
             ["The practice of using multiple public clouds (e.g., AWS and Azure).",
              "The practice of using a mix of public cloud and on-premises infrastructure.",
              "The practice of deploying an application across multiple regions.",
              "A strategy that uses \"hybrid\" virtual machines.",
              "A strategy for migrating applications."],
             1, "Hybrid cloud combines public cloud services with on-premises infrastructure."),
            
            ('What is the "Cloud Adoption Framework" (CAF)?',
             ["A specific piece of software for migrating to the cloud.",
              "A set of best practices and guidance from a cloud provider to help plan and execute a migration.",
              "A security-only framework for locking down cloud accounts.",
              "A sales and marketing framework for selling cloud services.",
              "A legal document required to open a cloud account."],
             1, "CAF provides best practices and guidance for planning and executing cloud migrations."),
            
            ('What is "cloud-native" architecture?',
             ["An architecture that avoids using any cloud provider-specific services.",
              "An architecture that is designed specifically to leverage cloud services, like serverless, containers, and microservices.",
              "An architecture that was \"born\" in the cloud (i.e., a new company).",
              "An architecture that is lifted-and-shifted from on-premises.",
              "An architecture that runs on a private cloud."],
             1, "Cloud-native architectures leverage cloud services like serverless, containers, and microservices."),
            
            ('What is a "Zero Trust" security model?',
             ["A model where you \"trust no one\" on your team.",
              "A model where you \"trust\" all devices inside the network, but \"zero\" outside.",
              "A security model based on the principle of \"never trust, always verify,\" treating all users and devices as untrusted.",
              "A model with \"zero\" firewalls.",
              "A model that has \"zero\" cost."],
             2, "Zero Trust assumes no implicit trust - all users and devices must be verified."),
            
            ('What is "cloud governance"?',
             ["The process of \"governing\" a country using cloud data.",
              "The set of policies, rules, and controls to manage costs, security, and compliance in the cloud.",
              "A specific cloud service for monitoring.",
              "A team of people who approve cloud accounts.",
              "A legal agreement with a cloud provider."],
             1, "Cloud governance establishes policies and controls for cost, security, and compliance."),
            
            ('What is a "FinOps" (Cloud Financial Operations)?',
             ["A \"finance\" team that operates in the cloud.",
              "A cultural practice that brings financial accountability to the variable spending model of the cloud.",
              "A specific tool for tracking cloud costs.",
              "A type of security audit.",
              "A model for \"financing\" a cloud migration."],
             1, "FinOps brings financial accountability and optimization to cloud spending."),
            
            ('What is a "Data Lake"?',
             ["A central repository that stores raw, unstructured and structured data at any scale.",
              "A central repository that stores only structured, cleaned data for analysis (this is a Data Warehouse).",
              "A type of NoSQL database.",
              "A service for monitoring data.",
              "A physical lake used to cool a data center."],
             0, "Data Lakes store raw, unstructured, and structured data at scale."),
            
            ('What is a "serverless" architecture (e.g., using Lambda, API Gateway, DynamoDB)?',
             ["An architecture where all the code runs on the client's browser.",
              "An architecture where you only use virtual machines.",
              "An architecture where you only use containers.",
              "An architecture composed of event-driven services where you don't manage any servers.",
              "An architecture that is not \"production-ready.\""],
             3, "Serverless architectures use event-driven services without managing servers."),
            
            ('What is the strategic trade-off of using a managed service (e.g., AWS RDS)?',
             ["Pro: Full control over the OS. Con: You must manage patching.",
              "Pro: Reduced operational overhead. Con: Less control and potential vendor lock-in.",
              "Pro: It is always cheaper. Con: It is less secure.",
              "Pro: It is more secure. Con: It is always slower.",
              "There are no trade-offs; they are always better."],
             1, "Managed services reduce ops overhead but sacrifice control and may create lock-in."),
            
            ('What is a "blue-green" deployment strategy?',
             ["A strategy where you deploy to \"blue\" (test) and \"green\" (prod) servers at the same time.",
              "A strategy where you have two identical environments (blue/green), deploy to the inactive one, and then switch traffic.",
              "A strategy that uses \"blue\" (fast) and \"green\" (eco-friendly) servers.",
              "A strategy for slowly rolling out a new feature to users.",
              "A strategy for database backups."],
             1, "Blue-green deployments maintain two identical environments and switch traffic after deployment."),
            
            ('What is a "canary release" strategy?',
             ["A strategy where you deploy a new version to all users at once.",
              "A strategy where you deploy a new version to a small subset of users, monitor it, and then roll it out to everyone.",
              "A strategy where you \"warn\" users (like a canary in a coal mine) before deploying.",
              "A strategy where you deploy two versions (A and B) at the same time.",
              "A strategy for database disaster recovery."],
             1, "Canary releases deploy to a small user subset first, then gradually roll out to all users."),
        ]
        
        quiz_5 = models.Quiz(
            title="Cloud Engineering - Strategic & Architectural",
            description="Strategic cloud: HA/DR, migration strategies, RPO/RTO, Reserved/Spot instances, multi/hybrid cloud, CAF, cloud-native, Zero Trust, governance, FinOps, deployment strategies",
            specialization_id=specialization.id,
            difficulty_level=5,
            time_limit_minutes=40
        )
        db.add(quiz_5)
        db.flush()
        
        for idx, (question_text, options, correct_idx, explanation) in enumerate(level_5_questions):
            question = models.Question(
                quiz_id=quiz_5.id,
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
        
        print(f"Added Level 5 (Strategic & Architectural): {len(level_5_questions)} questions")
        
        db.commit()
        print("\n✅ Successfully added Cloud Engineering quizzes (Levels 4-5 complete!)")
        print(f"Total questions added: {len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_cloud_engineering_advanced_quizzes()
