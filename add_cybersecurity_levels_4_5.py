"""
Add Cybersecurity Quizzes - Levels 4 and 5
This script adds 40 questions for Cybersecurity specialization (Expert through Strategic)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_cybersecurity_advanced_quizzes():
    db = SessionLocal()
    try:
        # Get Cybersecurity specialization
        specialization = db.query(models.Specialization).filter(
            models.Specialization.name == "Cybersecurity Analyst / InfoSec Analyst"
        ).first()
        
        if not specialization:
            print("Error: Cybersecurity Analyst / InfoSec Analyst specialization not found")
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
            ("What is a 'SIEM' (Security Information and Event Management) system?",
             ["A tool that collects, aggregates, and analyzes security log data from across an organization to detect threats.",
              "A tool for performing penetration tests.",
              "A type of firewall.",
              "A system for managing employee passwords.",
              "A hardware-based encryption device."],
             0, "SIEM systems centralize security data collection and analysis to detect threats across an organization."),
            
            ("What is 'Threat Intelligence'?",
             ["Information about an organization's internal security threats.",
              "Evidence-based knowledge (e.g., context, mechanisms, indicators) about existing or emerging threats, which can be used to inform security decisions.",
              "A type of AI that is a 'threat'.",
              "A list of all company vulnerabilities.",
              "A tool for performing DDoS attacks."],
             1, "Threat Intelligence provides actionable knowledge about threats to inform security decisions and defenses."),
            
            ("What is the 'Cyber Kill Chain'?",
             ["A model (by Lockheed Martin) that outlines the stages of a cyberattack, from reconnaissance to post-exploitation.",
              "A piece of malware that 'kills' a network.",
              "A tool for 'killing' viruses.",
              "A security policy.",
              "A type of encryption."],
             0, "The Cyber Kill Chain maps attack stages: reconnaissance, weaponization, delivery, exploitation, installation, C2, and actions."),
            
            ("What is 'sandboxing'?",
             ["The practice of testing code on a beach.",
              "A security mechanism for running suspicious programs in a separate, isolated environment to see what they do.",
              "A type of network firewall.",
              "A method for storing passwords.",
              "A type of penetration test."],
             1, "Sandboxing isolates suspicious programs to safely analyze their behavior without risking the main system."),
            
            ("What is 'digital forensics'?",
             ["The process of building secure digital systems.",
              "The practice of collecting, analyzing, and preserving digital evidence in a way that is legally admissible.",
              "A type of antivirus software.",
              "A method for performing DDoS attacks.",
              "A type of encryption."],
             1, "Digital forensics involves collecting and preserving digital evidence for legal investigations."),
            
            ("What is the 'MITRE ATT&CK' framework?",
             ["A globally accessible knowledge base of adversary tactics and techniques based on real-world observations.",
              "A specific piece of attack software.",
              "A security compliance standard, like PCI.",
              "A type of firewall.",
              "A tool for penetration testing."],
             0, "MITRE ATT&CK is a knowledge base documenting real-world adversary tactics, techniques, and procedures."),
            
            ("What is 'Incident Response' (IR)?",
             ["The process of responding to all emails and support tickets.",
              "An organization's formal plan and methodology for handling a security breach or cyberattack.",
              "A tool that blocks attacks.",
              "The process of patching software.",
              "The process of backing up data."],
             1, "Incident Response is the structured approach to handling security breaches and cyberattacks."),
            
            ("What is a 'Web Application Firewall' (WAF)?",
             ["A firewall that protects a user's web browser.",
              "A firewall that filters, monitors, and blocks HTTP traffic to and from a web application (e.g., to block SQLi and XSS).",
              "A firewall built into the Windows operating system.",
              "A type of antivirus software.",
              "A physical hardware device."],
             1, "WAFs protect web applications by filtering and monitoring HTTP traffic to block attacks like SQLi and XSS."),
            
            ("What is 'container security'?",
             ["The practice of securing physical shipping containers.",
              "The practice of securing software 'containers' (e.g., Docker, Kubernetes) and their lifecycle.",
              "A type of firewall.",
              "A method for securing backups.",
              "A type of physical security."],
             1, "Container security involves securing containerized applications (Docker, Kubernetes) throughout their lifecycle."),
            
            ("What is a 'Security Operations Center' (SOC)?",
             ["A command center facility where a team of security professionals monitors and analyzes an organization's security posture.",
              "A piece of software for securing a PC.",
              "A type of security attack.",
              "A secure data backup location.",
              "A type of encryption."],
             0, "A SOC is a centralized facility where security teams monitor, detect, and respond to threats 24/7."),
            
            ("What is 'OAuth 2.0'?",
             ["A protocol for authentication (proving who you are).",
              "An open standard for delegated authorization, allowing apps to access resources on behalf of a user (e.g., 'Sign in with Google').",
              "A type of encryption.",
              "A specific type of security attack.",
              "A version of a firewall."],
             1, "OAuth 2.0 enables secure delegated authorization, allowing apps to access resources without sharing passwords."),
            
            ("What is 'Server-Side Request Forgery' (SSRF)?",
             ["An attack where an attacker forges a request from a client.",
              "A vulnerability where an attacker can induce a server-side application to make requests to an unintended location.",
              "A type of XSS attack.",
              "A type of SQL Injection attack.",
              "A tool for testing servers."],
             1, "SSRF exploits server-side applications to make unauthorized requests to internal or external systems."),
            
            ("What is a 'vulnerability scan'?",
             ["An automated process that scans a system for known vulnerabilities (e.g., missing patches, misconfigurations).",
              "A manual process of trying to exploit vulnerabilities (this is a pen test).",
              "A scan for viruses.",
              "A scan for hardware errors.",
              "A scan for user passwords."],
             0, "Vulnerability scans automatically identify known vulnerabilities, missing patches, and misconfigurations."),
            
            ("What is 'Network Access Control' (NAC)?",
             ["A policy that denies all access to the network.",
              "A security approach that attempts to unify endpoint security (e.g., antivirus, patches) with network security and access control.",
              "A type of VPN.",
              "A type of firewall.",
              "A tool for monitoring network speed."],
             1, "NAC enforces security policies by controlling which devices can access the network based on their security posture."),
            
            ("What is a 'password-spraying' attack?",
             ["An attack that tries many different passwords for a single username.",
              "An attack that tries a single, common password against many different usernames.",
              "An attack where a user 'sprays' their password on a wall.",
              "A tool for generating strong passwords.",
              "A type of ransomware."],
             1, "Password spraying tries common passwords against many accounts to avoid account lockouts from brute force."),
            
            ("What is 'credential stuffing'?",
             ["The act of 'stuffing' credentials into a secure vault.",
              "An attack where stolen usernames and passwords from one data breach are used to try and log in to other services.",
              "A type of password-spraying attack.",
              "A security feature.",
              "A tool for penetration testers."],
             1, "Credential stuffing reuses breached credentials from one service to gain access to other services."),
            
            ("What is 'threat modeling'?",
             ["A process for building a model of a computer network.",
              "A structured process for identifying, quantifying, and addressing potential threats and vulnerabilities in a system during its design phase.",
              "A tool for creating 'honeypots'.",
              "A method for responding to an incident.",
              "A type of security compliance."],
             1, "Threat modeling systematically identifies and addresses security threats during system design."),
            
            ("What is 'SOAR' (Security Orchestration, Automation, and Response)?",
             ["A tool that replaces a SIEM.",
              "A platform that helps security teams manage and respond to alarms by automating and orchestrating security workflows.",
              "A type of security attack.",
              "A physical security device.",
              "A compliance standard."],
             1, "SOAR platforms automate and orchestrate security workflows to improve incident response efficiency."),
            
            ("What is 'fuzzing'?",
             ["An automated testing technique that provides invalid, unexpected, or random data as input to a program to find bugs.",
              "A manual testing technique.",
              "A type of social engineering attack.",
              "A method for encrypting data.",
              "A type of network scan."],
             0, "Fuzzing automatically tests software by providing invalid or random inputs to discover vulnerabilities."),
            
            ("What is 'reverse engineering' in a malware context?",
             ["The process of building new malware.",
              "The process of decompiling and analyzing a piece of malware to understand what it does and how it works.",
              "A type of security attack.",
              "A method for patching software.",
              "The process of designing a secure system in reverse."],
             1, "Reverse engineering malware involves analyzing its code to understand its functionality and behavior."),
        ]
        
        quiz_4 = models.Quiz(
            title="Cybersecurity - Expert & Specialization",
            description="Expert security: SIEM, threat intelligence, incident response, WAF, SOC, OAuth, SSRF, and advanced tools",
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
            ("What is 'Governance, Risk, and Compliance' (GRC)?",
             ["A specific type of security software.",
              "A structured approach to aligning an organization's IT with its business goals, while managing risks and meeting compliance requirements.",
              "A team of hackers (Red Team).",
              "A model for a cyberattack.",
              "A type of firewall."],
             1, "GRC aligns IT with business objectives while managing security risks and meeting regulatory compliance."),
            
            ("What is a 'Business Continuity Plan' (BCP)?",
             ["A plan for how a business will continue to operate during and after a disaster.",
              "A plan for how to stop a cyberattack.",
              "A plan for how to back up data.",
              "A plan for how to patch servers.",
              "A plan for the company's 'continuity' party."],
             0, "BCP ensures business operations can continue during and after disasters or disruptions."),
            
            ("What is a 'Disaster Recovery' (DR) plan?",
             ["A plan focused specifically on restoring the IT infrastructure and data after a disaster. (It is a part of the BCP).",
              "A plan for firing employees after a disaster.",
              "A plan for preventing disasters.",
              "A plan for managing security risks.",
              "A plan for a company's financial recovery."],
             0, "DR plans focus on restoring IT systems and data after disasters, as part of broader BCP."),
            
            ("What is a 'security risk assessment'?",
             ["The process of identifying, analyzing, and evaluating risks to an organization's assets.",
              "The process of buying insurance for a security risk.",
              "A list of all company assets.",
              "A tool that blocks all risks.",
              "A penetration test."],
             0, "Risk assessments systematically identify, analyze, and evaluate security risks to organizational assets."),
            
            ("What is the difference between 'quantitative' and 'qualitative' risk analysis?",
             ["Quantitative uses numerical values (e.g., money); Qualitative uses descriptive categories (e.g., high, medium, low).",
              "Quantitative is for 'quantity' of risks; Qualitative is for 'quality' of risks.",
              "Quantitative is fast; Qualitative is slow.",
              "Quantitative is for hardware; Qualitative is for software.",
              "There is no difference."],
             0, "Quantitative analysis uses numerical metrics; qualitative uses descriptive categories for risk evaluation."),
            
            ("What is 'defense in depth'?",
             ["A security strategy that relies on a single, very strong defense (like a firewall).",
              "A security strategy that uses multiple, layered security controls, so if one fails, another may stop the attack.",
              "A type of military strategy.",
              "A strategy for 'deeply' analyzing a threat.",
              "A type of data backup."],
             1, "Defense in depth uses multiple layered security controls to protect against failures of any single layer."),
            
            ("What is 'ISO 27001'?",
             ["A specific type of firewall.",
              "An international standard that specifies the requirements for an Information Security Management System (ISMS).",
              "A US government law.",
              "A type of encryption.",
              "A piece of hacking software."],
             1, "ISO 27001 is an international standard for implementing and managing information security management systems."),
            
            ("What is 'PCI DSS'?",
             ["A 'Payment Card Industry Data Security Standard,' a set of requirements for any organization that handles credit card data.",
              "A 'Personal Computer Information' standard.",
              "A government law for data privacy.",
              "A type of antivirus software.",
              "A standard for building secure PCs."],
             0, "PCI DSS mandates security requirements for organizations that process, store, or transmit credit card data."),
            
            ("What is 'HIPAA'?",
             ["A US law (Health Insurance Portability and Accountability Act) that includes rules for protecting the privacy and security of patient health information.",
              "A security standard for banks.",
              "A type of encryption.",
              "A type of 'hippopotamus' virus.",
              "A European data privacy law."],
             0, "HIPAA is US legislation protecting the privacy and security of patient health information."),
            
            ("What is 'GDPR'?",
             ["A US data privacy law.",
              "A 'General Data Protection Regulation' - a European Union law on data protection and privacy.",
              "A 'General Data Risk' policy.",
              "A standard for building secure networks.",
              "A type of security attack."],
             1, "GDPR is the EU's comprehensive data protection and privacy regulation for EU citizens."),
            
            ("What is a 'Chief Information Security Officer' (CISO)?",
             ["The senior-level executive responsible for an organization's entire information security program.",
              "The lead developer on the security team.",
              "A consultant who performs penetration tests.",
              "A government agent in charge of cybersecurity.",
              "The person who manages the firewall."],
             0, "The CISO is the executive responsible for an organization's information security strategy and program."),
            
            ("What is 'security architecture'?",
             ["The physical architecture of a secure building.",
              "The design of a secure IT system, based on security principles, to protect assets and manage risk.",
              "A diagram of a network.",
              "A list of security rules.",
              "A type of firewall."],
             1, "Security architecture designs IT systems based on security principles to protect assets and manage risks."),
            
            ("What is a 'Zero Trust' security model?",
             ["A model where you 'trust no one' on your team.",
              "A model where you 'trust' all devices inside the network, but 'zero' outside.",
              "A security model based on the principle of 'never trust, always verify,' treating all users and devices as untrusted.",
              "A model with 'zero' firewalls.",
              "A model that has 'zero' cost."],
             2, "Zero Trust assumes no implicit trust - all users and devices must be verified regardless of location."),
            
            ("What is a 'supply chain' attack in cybersecurity?",
             ["An attack on a company's physical shipping and logistics.",
              "An attack where an attacker compromises a trusted third-party vendor (e.g., a software supplier) to gain access to the real target.",
              "An attack on a grocery store's supply chain.",
              "A type of phishing attack.",
              "A type of DDoS attack."],
             1, "Supply chain attacks compromise trusted third-party vendors to access the ultimate target organization."),
            
            ("What are the key phases of an 'Incident Response' plan?",
             ["1. Preparation, 2. Identification, 3. Containment, 4. Eradication, 5. Recovery, 6. Lessons Learned.",
              "1. Attack, 2. Defend, 3. Win.",
              "1. Blame, 2. Fire, 3. Hire.",
              "1. Detect, 2. Delete, 3. Restore.",
              "1. Call the CEO, 2. Call the police, 3. Call the news."],
             0, "IR phases: Preparation, Identification, Containment, Eradication, Recovery, and Lessons Learned."),
            
            ("What is 'threat hunting'?",
             ["The proactive and iterative process of searching through networks and datasets to detect and isolate advanced threats that evade existing security tools.",
              "The reactive process of responding to a security alert.",
              "A type of penetration test.",
              "A type of social engineering.",
              "A tool for 'hunting' for files."],
             0, "Threat hunting proactively searches for advanced threats that bypass automated security tools."),
            
            ("What is 'Cloud Security Posture Management' (CSPM)?",
             ["A tool for managing employee posture (sitting) in the cloud.",
              "A class of tools designed to identify and remediate misconfigurations and compliance risks in cloud environments.",
              "A type of cloud firewall.",
              "A cloud-based antivirus.",
              "A cloud provider's physical security."],
             1, "CSPM tools identify and fix misconfigurations and compliance issues in cloud infrastructure."),
            
            ("What is 'Business Email Compromise' (BEC)?",
             ["A type of malware that compromises an email server.",
              "A type of phishing attack.",
              "An attack where an attacker gains access to a business email account and impersonates the owner to defraud the company.",
              "A security tool for scanning emails.",
              "A compliance standard for emails."],
             2, "BEC involves compromising business email accounts to impersonate executives and defraud organizations."),
            
            ("What is a 'purple team'?",
             ["A team that is a mix of managers and engineers.",
              "A team that works to foster communication and collaboration between the Red Team (attack) and Blue Team (defense).",
              "A team of external consultants.",
              "A compliance and audit team.",
              "A team that develops security software."],
             1, "Purple teams facilitate collaboration between red (offensive) and blue (defensive) teams to improve security."),
            
            ("What is 'cyber resilience'?",
             ["The ability of an organization to resist all cyberattacks so they never fail.",
              "The ability of an organization to prepare for, respond to, and recover from a cyberattack, while continuing to operate.",
              "A type of antivirus software.",
              "A type of insurance policy.",
              "A government agency."],
             1, "Cyber resilience is the ability to maintain operations during and recover from cyberattacks."),
        ]
        
        quiz_5 = models.Quiz(
            title="Cybersecurity - Strategic & Architectural",
            description="Strategic security: GRC, compliance (GDPR, HIPAA, PCI DSS), Zero Trust, incident response, threat hunting, and cyber resilience",
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
        print("\n✅ Successfully added Cybersecurity quizzes (Levels 4-5 complete!)")
        print(f"Total questions added: {len(level_4_questions) + len(level_5_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_cybersecurity_advanced_quizzes()
