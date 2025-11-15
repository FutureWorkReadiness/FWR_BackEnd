"""
Add Cybersecurity Quizzes - Levels 1, 2, and 3
This script adds 60 questions for Cybersecurity specialization (Basic through Advanced)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models_hierarchical as models

def add_cybersecurity_quizzes():
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
            ("What is 'Cybersecurity'?",
             ["The practice of repairing computers and servers.",
              "The practice of protecting systems, networks, and data from digital attacks.",
              "The practice of writing code for websites.",
              "The practice of analyzing business data.",
              "The practice of creating computer networks."],
             1, "Cybersecurity is the practice of protecting systems, networks, and data from digital attacks and threats."),
            
            ("What is 'malware'?",
             ["A general term for any malicious software designed to cause harm or gain unauthorized access.",
              "A specific type of computer hardware.",
              "A secure piece of code that protects a computer.",
              "A computer network.",
              "A user's password."],
             0, "Malware is malicious software designed to damage, disrupt, or gain unauthorized access to systems."),
            
            ("What is a 'virus'?",
             ["A piece of code that protects a file.",
              "A malicious program that attaches itself to legitimate files and spreads when they are opened.",
              "A piece of hardware that speeds up a computer.",
              "A secure login screen.",
              "A network connection."],
             1, "A virus is malware that attaches to files and spreads when those files are executed."),
            
            ("What is a 'firewall'?",
             ["A program that finds and deletes viruses.",
              "A network security device that monitors and filters incoming and outgoing network traffic.",
              "A type of malicious software.",
              "A physical wall in a server room to prevent fires.",
              "A tool for writing code."],
             1, "A firewall monitors and controls network traffic based on security rules to protect networks."),
            
            ("What is 'phishing'?",
             ["A method of securing an email account.",
              "A fraudulent attempt to obtain sensitive information (like passwords or credit card numbers) by disguising as a trustworthy entity in an email or message.",
              "A type of computer virus.",
              "A secure way to back up files.",
              "A tool for catching network traffic."],
             1, "Phishing is a social engineering attack that tricks users into revealing sensitive information."),
            
            ("What does the 'C' in the 'CIA Triad' stand for?",
             ["Cybersecurity", "Confidentiality", "Compliance", "Computer", "Code"],
             1, "The CIA Triad consists of Confidentiality, Integrity, and Availability - core security principles."),
            
            ("What does the 'I' in the 'CIA Triad' stand for?",
             ["Integrity", "Internet", "Information", "Intrusion", "Identity"],
             0, "Integrity ensures data remains accurate and unaltered except by authorized parties."),
            
            ("What does the 'A' in the 'CIA Triad' stand for?",
             ["Attack", "Authentication", "Availability", "Access", "Antivirus"],
             2, "Availability ensures authorized users have reliable access to systems and data when needed."),
            
            ("What is 'authentication'?",
             ["The process of protecting a network with a firewall.",
              "The process of verifying the identity of a user (proving you are who you say you are).",
              "The process of giving a user permission to access a file.",
              "The process of encrypting data.",
              "The process of attacking a system."],
             1, "Authentication verifies a user's identity through credentials like passwords, biometrics, or tokens."),
            
            ("What is 'authorization'?",
             ["The process of verifying a user's identity.",
              "The process of determining what a user is allowed to do or access after they have been authenticated.",
              "The process of scanning for viruses.",
              "The process of writing a security policy.",
              "The process of backing up data."],
             1, "Authorization determines what authenticated users are permitted to access or do in a system."),
            
            ("What is a 'strong password'?",
             ["A short, easy-to-remember password like '12345'.",
              "A long, complex password with a mix of upper/lowercase letters, numbers, and symbols.",
              "A password that is written down on a sticky note.",
              "A password that is the same as your username.",
              "A password that is a single, common dictionary word."],
             1, "Strong passwords are long, complex, and use a mix of characters to resist guessing attacks."),
            
            ("What is 'antivirus' software?",
             ["A program designed to detect, prevent, and remove malicious software.",
              "A type of malware.",
              "A network firewall.",
              "A tool for sending phishing emails.",
              "A hardware device."],
             0, "Antivirus software scans for, blocks, and removes malicious software from systems."),
            
            ("What is 'encryption'?",
             ["The process of deleting data permanently.",
              "The process of converting data into a secret code to prevent unauthorized access.",
              "The process of stealing data.",
              "The process of finding viruses.",
              "The process of creating a backup."],
             1, "Encryption transforms data into an unreadable format that requires a key to decrypt."),
            
            ("What is a 'patch'?",
             ["A type of computer virus.",
              "A software update released by a vendor to fix a bug or security vulnerability.",
              "A piece of hardware.",
              "A fraudulent email.",
              "A weak password."],
             1, "Patches are software updates that fix vulnerabilities and bugs to improve security and functionality."),
            
            ("What is a 'vulnerability'?",
             ["A strong security setting.",
              "A piece of antivirus software.",
              "A weakness in a system that an attacker could exploit.",
              "A user's password.",
              "A backup of your data."],
             2, "Vulnerabilities are weaknesses in systems, software, or processes that attackers can exploit."),
            
            ("What is 'social engineering'?",
             ["A security hardware device.",
              "The act of psychologically manipulating people into performing actions or divulging confidential information.",
              "The process of engineering a secure network.",
              "A type of encryption.",
              "A tool for scanning for viruses."],
             1, "Social engineering manipulates human psychology to trick people into breaking security procedures."),
            
            ("What is a 'backup'?",
             ["A copy of data that can be used to restore the original in case of data loss.",
              "A type of malware.",
              "A firewall.",
              "A security vulnerability.",
              "A user's login name."],
             0, "Backups are copies of data stored separately to enable recovery after data loss or corruption."),
            
            ("What is a 'username'?",
             ["A secret code used to encrypt files.",
              "A type of computer virus.",
              "A name that uniquely identifies someone on a computer system.",
              "A piece of malicious software.",
              "A secure network."],
             2, "A username is a unique identifier for a user account on a system or network."),
            
            ("What is a 'hacker'?",
             ["Someone who sells computer hardware.",
              "An individual who uses computer, networking, or other skills to overcome a technical problem. (Can be ethical or malicious).",
              "A software program that deletes files.",
              "A customer support agent.",
              "A type of computer server."],
             1, "A hacker is someone with technical skills to overcome problems - can be ethical (white hat) or malicious (black hat)."),
            
            ("What is 'data'?",
             ["A physical computer.",
              "Information, such as facts or numbers, that can be stored and used.",
              "A type of antivirus software.",
              "A network firewall.",
              "A security attack."],
             1, "Data is information in various forms that can be processed, stored, and transmitted by computers."),
        ]
        
        quiz_1 = models.Quiz(
            title="Cybersecurity - Basic Foundations",
            description="Fundamental security concepts: CIA Triad, malware types, authentication, encryption, and basic threats",
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
            ("What is the main difference between a 'virus' and a 'worm'?",
             ["A virus is malicious, but a worm is not.",
              "A virus needs a host file to spread; a worm can self-replicate and spread across a network independently.",
              "A virus spreads through email; a worm spreads through websites.",
              "A virus is hardware; a worm is software.",
              "There is no difference."],
             1, "Viruses require host files to spread, while worms self-replicate and spread independently across networks."),
            
            ("What is 'ransomware'?",
             ["A type of malware that encrypts a victim's files and demands a ransom payment to decrypt them.",
              "A security tool that 'ransoms' a hacker's computer.",
              "A hardware device for encrypting files.",
              "A type of antivirus software.",
              "A free software update."],
             0, "Ransomware encrypts files and demands payment for the decryption key, holding data hostage."),
            
            ("What is a 'Trojan' in cybersecurity?",
             ["A security program from Troy.",
              "Malware that disguises itself as legitimate software (like a game or utility) to trick a user into running it.",
              "A type of computer hardware.",
              "A network firewall rule.",
              "A secure backup file."],
             1, "Trojans disguise themselves as legitimate software to trick users into installing malware."),
            
            ("What is a 'VPN' (Virtual Private Network)?",
             ["A type of computer virus.",
              "A secure, encrypted connection over a public network, used to protect privacy and secure data.",
              "A public, open Wi-Fi network.",
              "A tool for designing websites.",
              "A type of malicious software."],
             1, "VPNs create encrypted tunnels over public networks to protect privacy and secure communications."),
            
            ("What is 'Two-Factor Authentication' (2FA)?",
             ["Using two different computers to log in.",
              "A security process that requires two different methods of authentication (e.g., a password and a code from your phone).",
              "Using two different passwords for the same account.",
              "A type of firewall.",
              "A type of virus."],
             1, "2FA requires two different authentication factors (something you know + something you have) for stronger security."),
            
            ("What is the main difference between 'hashing' and 'encryption'?",
             ["Hashing is reversible; encryption is not.",
              "Hashing is for text; encryption is for files.",
              "Hashing is a one-way function (cannot be reversed); encryption is a two-way function (can be decrypted with a key).",
              "Hashing is insecure; encryption is secure.",
              "They are the same thing."],
             2, "Hashing is one-way and irreversible; encryption is two-way and can be decrypted with the proper key."),
            
            ("Why is it important to 'patch' software?",
             ["To change the color and design.",
              "To fix security vulnerabilities before attackers can exploit them.",
              "To make the software run slower.",
              "To delete old files.",
              "It is not important."],
             1, "Patches fix security vulnerabilities to prevent exploitation by attackers."),
            
            ("What is 'HTTPS'?",
             ["A faster, 'hyper' version of HTTP.",
              "The secure version of HTTP; it encrypts the data sent between your browser and the website.",
              "A type of malware.",
              "A standard for writing HTML code.",
              "A type of firewall."],
             1, "HTTPS encrypts web traffic using SSL/TLS to protect data between browsers and websites."),
            
            ("What is a 'DDoS' attack?",
             ["A 'Distributed Denial-of-Service' attack, where an attacker floods a server with traffic from many sources to overwhelm it.",
              "A 'Data Deletion of Service' attack, where an attacker deletes all files.",
              "A security tool for 'Detecting and Denying' attacks.",
              "A type of antivirus software.",
              "A method for backing up a server."],
             0, "DDoS attacks overwhelm servers with traffic from multiple sources to make them unavailable."),
            
            ("What is a 'botnet'?",
             ["A network of secure computers used for research.",
              "A network of private computers infected with malicious software and controlled as a group by an attacker.",
              "A type of fishing net for robots.",
              "A security company's internal network.",
              "An antivirus program."],
             1, "Botnets are networks of compromised computers controlled by attackers for malicious purposes."),
            
            ("What is 'spyware'?",
             ["Software that 'spies' on your computer, secretly monitoring your activity and collecting personal information.",
              "A tool used by security professionals to spy on hackers.",
              "A type of hardware device.",
              "A secure web browser.",
              "A password manager."],
             0, "Spyware secretly monitors user activity and collects personal information without consent."),
            
            ("What does a 'password manager' do?",
             ["It generates weak, easy-to-guess passwords.",
              "It securely stores all your unique, complex passwords in an encrypted vault.",
              "It is a type of malware that steals passwords.",
              "It is a spreadsheet for typing passwords into.",
              "It is a hardware device for locking your computer."],
             1, "Password managers securely store and encrypt all passwords, enabling use of unique, complex passwords."),
            
            ("What is the 'Principle of Least Privilege'?",
             ["The idea that important people ('princes') get the most access.",
              "The idea that users and programs should only be given the minimum permissions necessary to perform their job.",
              "The idea that all users should have admin access.",
              "A law that requires all software to be free.",
              "A type of security attack."],
             1, "Least Privilege grants users only the minimum permissions needed, reducing security risk."),
            
            ("What is a 'security policy'?",
             ["A type of firewall.",
              "A document that outlines an organization's rules and procedures for information security.",
              "A piece of malicious software.",
              "A tool for hacking.",
              "A computer's hardware."],
             1, "Security policies document an organization's security rules, procedures, and standards."),
            
            ("What is the main difference between 'symmetric' and 'asymmetric' encryption?",
             ["Symmetric is fast; asymmetric is slow.",
              "Symmetric uses one single key for both encryption and decryption; asymmetric uses two keys (a public and a private key).",
              "Symmetric is secure; asymmetric is not.",
              "Symmetric is new; asymmetric is old.",
              "Symmetric is for files; asymmetric is for text."],
             1, "Symmetric uses one shared key; asymmetric uses a public key pair (public and private keys)."),
            
            ("What is a 'digital certificate'?",
             ["A type of malware.",
              "A digital file used to prove the identity of a website or individual (e.g., used in HTTPS).",
              "A certificate you get for completing a cybersecurity course.",
              "A password.",
              "A firewall."],
             1, "Digital certificates verify the identity of websites and individuals, enabling secure HTTPS connections."),
            
            ("What is 'BYOD'?",
             ["'Bring Your Own Device' - A policy allowing employees to use their personal devices for work.",
              "'Buy Your Own Data' - A policy for internet usage.",
              "'Backup Your Own Data' - A backup policy.",
              "'Block Your Own Device' - A security attack.",
              "A type of antivirus software."],
             0, "BYOD policies allow employees to use personal devices for work, requiring security considerations."),
            
            ("What is a 'security risk' of public Wi-Fi?",
             ["It is usually too slow.",
              "It costs too much money.",
              "Attackers can 'sniff' the traffic, intercepting unencrypted data like passwords or credit card numbers.",
              "It is not compatible with most new devices.",
              "There is no risk; all public Wi-Fi is secure."],
             2, "Public Wi-Fi traffic can be intercepted by attackers sniffing unencrypted data on the network."),
            
            ("What is 'adware'?",
             ["Software that securely blocks all advertisements.",
              "Software that automatically downloads and installs security 'add-ons'.",
              "Software that displays unwanted pop-up advertisements.",
              "A hardware device for advertising.",
              "A type of secure web browser."],
             2, "Adware displays unwanted advertisements, often bundled with free software."),
            
            ("What is 'data breach'?",
             ["A successful security incident in which sensitive, confidential, or protected data is stolen or accessed by an unauthorized person.",
              "The process of backing up data.",
              "The process of encrypting data.",
              "A type of firewall.",
              "A software patch."],
             0, "A data breach occurs when unauthorized parties access, steal, or expose sensitive data."),
        ]
        
        quiz_2 = models.Quiz(
            title="Cybersecurity - Intermediate Application",
            description="Intermediate security: malware types, VPNs, 2FA, encryption methods, DDoS, and security policies",
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
            ("What is a 'SQL Injection' (SQLi) attack?",
             ["An attack where a user 'injects' JavaScript into a website.",
              "An attack where an attacker inserts malicious SQL code into a web form to manipulate the backend database.",
              "A method for 'injecting' more speed into a database.",
              "A type of secure database query.",
              "A tool for cleaning a database."],
             1, "SQL Injection exploits vulnerabilities by inserting malicious SQL code into input fields to manipulate databases."),
            
            ("How do you prevent a basic SQL Injection attack?",
             ["By using a strong firewall.",
              "By using prepared statements (parameterized queries) and input validation.",
              "By encrypting the entire database.",
              "By using HTTPS.",
              "By hiding the web form from users."],
             1, "Prevent SQL Injection with prepared statements, parameterized queries, and input validation."),
            
            ("What is a 'Cross-Site Scripting' (XSS) attack?",
             ["An attack where malicious code is injected into a trusted website, which then runs in a victim's browser.",
              "An attack where an attacker 'crosses' two different websites.",
              "An attack that steals a website's CSS files.",
              "An attack that targets the server's database.",
              "A method for securing a website."],
             0, "XSS injects malicious scripts into trusted websites that execute in victims' browsers."),
            
            ("What is the difference between 'Stored XSS' and 'Reflected XSS'?",
             ["Stored XSS is permanent; Reflected XSS is temporary.",
              "Stored XSS is saved on the server (e.g., in a comment); Reflected XSS is sent in a request (e.g., a URL) and reflected back.",
              "Stored XSS is harmless; Reflected XSS is dangerous.",
              "Stored XSS is for databases; Reflected XSS is for websites.",
              "There is no difference."],
             1, "Stored XSS persists on the server; Reflected XSS is returned immediately in the response."),
            
            ("What is a 'Man-in-the-Middle' (MITM) attack?",
             ["An attack where a hacker is 'in the middle' of two other hackers.",
              "An attack where an attacker secretly intercepts and relays communication between two parties who believe they are communicating directly.",
              "A security tool for monitoring network traffic.",
              "A type of firewall.",
              "A type of server."],
             1, "MITM attacks intercept communication between two parties to eavesdrop or manipulate data."),
            
            ("What is a 'zero-day' vulnerability?",
             ["A vulnerability that has zero impact.",
              "A vulnerability that is 'day zero' of a new software.",
              "A software vulnerability that is known to the vendor, but they have 'zero days' to fix it.",
              "A vulnerability that is discovered and exploited by hackers before the vendor is aware of it or can release a patch.",
              "A vulnerability that only exists for one day."],
             3, "Zero-day vulnerabilities are unknown to vendors and exploited before patches are available."),
            
            ("What is 'penetration testing' (or 'pen testing')?",
             ["The act of illegally hacking into a system.",
              "An authorized simulated cyberattack on a computer system to evaluate its security.",
              "A test to see if a pen will write on a computer.",
              "A type of antivirus software.",
              "A method for backing up a system."],
             1, "Penetration testing is authorized simulated hacking to identify security weaknesses."),
            
            ("What is the main difference between 'Red Team' and 'Blue Team'?",
             ["Red Team attacks a system; Blue Team defends it.",
              "Red Team is for hardware; Blue Team is for software.",
              "Red Team is for Windows; Blue Team is for Linux.",
              "Red Team is the 'bad guys'; Blue Team is the 'good guys'. (Note: Both are 'good guys' in a test).",
              "Red Team is for the network; Blue Team is for the computers."],
             0, "Red Team simulates attackers; Blue Team defends - both work together to improve security."),
            
            ("What is an 'IDS' (Intrusion Detection System)?",
             ["A system that only monitors network traffic and alerts an admin of suspicious activity.",
              "A system that actively blocks suspicious activity.",
              "A system for 'Installing, Deploying, and Securing' software.",
              "A type of firewall.",
              "A type of antivirus software."],
             0, "IDS monitors network traffic and alerts administrators to suspicious activity without blocking it."),
            
            ("What is an 'IPS' (Intrusion Prevention System)?",
             ["A system that only monitors and alerts.",
              "A system that monitors traffic and actively blocks detected threats.",
              "A system for 'Installing, Protecting, and Securing' software.",
              "A type of antivirus software.",
              "A password manager."],
             1, "IPS monitors traffic and actively blocks detected threats in real-time."),
            
            ("What is 'spear phishing'?",
             ["A phishing attack that targets a specific individual, group, or organization.",
              "A phishing attack that uses a 'spear' in the email.",
              "A general, non-targeted phishing email.",
              "A type of fishing.",
              "A type of secure email."],
             0, "Spear phishing is targeted phishing aimed at specific individuals or organizations."),
            
            ("What is 'whaling' in cybersecurity?",
             ["A spear phishing attack that specifically targets high-profile individuals like executives (CEOs, CFOs).",
              "An attack that targets fishing boats.",
              "A type of DDoS attack.",
              "A security tool for 'watching' network traffic.",
              "A type of firewall."],
             0, "Whaling targets high-profile executives with sophisticated spear phishing attacks."),
            
            ("What is a 'honeypot'?",
             ["A decoy computer system or server, set up to attract and trap attackers.",
              "A type of malware.",
              "A secure database for storing passwords.",
              "A social engineering technique.",
              "A type of firewall."],
             0, "Honeypots are decoy systems designed to attract attackers and study their tactics."),
            
            ("What is 'encryption key management'?",
             ["The process of managing the lifecycle of cryptographic keys (generation, storage, use, and deletion).",
              "The process of managing employee passwords.",
              "A type of software for typing.",
              "A hardware device for storing files.",
              "The process of encrypting and decrypting data."],
             0, "Key management handles the entire lifecycle of cryptographic keys from creation to destruction."),
            
            ("What is 'Cross-Site Request Forgery' (CSRF)?",
             ["An attack where a user is tricked into submitting a malicious request to a website they are already logged into.",
              "An attack where an attacker 'forges' a new website.",
              "An attack where an attacker injects a script (this is XSS).",
              "An attack that steals a database.",
              "A security tool for forging certificates."],
             0, "CSRF tricks authenticated users into unknowingly submitting malicious requests to web applications."),
            
            ("What is a 'rootkit'?",
             ["A type of malware designed to gain 'root' (admin) access to a computer and remain hidden.",
              "A tool for securing the 'root' directory.",
              "A type of antivirus software.",
              "A hardware device.",
              "A tool for penetration testers."],
             0, "Rootkits are stealthy malware that gain privileged access and hide their presence on systems."),
            
            ("What is 'hardening' a system?",
             ["The process of making a computer physically harder.",
              "The process of making a system more difficult to use.",
              "The process of securing a system by reducing its attack surface (e.g., disabling unused services, applying patches).",
              "The process of backing up a system.",
              "The process of installing a virus."],
             2, "Hardening secures systems by removing unnecessary services, applying patches, and reducing attack surface."),
            
            ("What is a 'VPN Concentrator'?",
             ["A device that terminates multiple VPN tunnels, typically used at a corporate headquarters.",
              "A piece of software on a user's laptop.",
              "A type of attack against VPNs.",
              "A protocol for securing VPNs.",
              "A tool for 'concentrating' on network traffic."],
             0, "VPN concentrators are devices that handle multiple VPN connections at enterprise scale."),
            
            ("What is 'data loss prevention' (DLP)?",
             ["The process of backing up data.",
              "A set of tools and policies designed to prevent sensitive data from leaving an organization's network.",
              "A type of encryption.",
              "A type of firewall.",
              "A method for recovering lost data."],
             1, "DLP tools and policies prevent unauthorized transmission of sensitive data outside the organization."),
            
            ("What is 'Access Control'?",
             ["The selective restriction of access to a resource; the implementation of 'authorization'.",
              "A type of password.",
              "A hardware device for opening a door.",
              "A type of malware.",
              "The process of logging in."],
             0, "Access Control restricts resource access based on user identity and permissions (authorization)."),
        ]
        
        quiz_3 = models.Quiz(
            title="Cybersecurity - Advanced Scenarios",
            description="Advanced security: SQL injection, XSS, CSRF, MITM, zero-day, pen testing, IDS/IPS, and advanced threats",
            specialization_id=specialization.id,
            difficulty_level=3,
            time_limit_minutes=30
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
        print("\n✅ Successfully added Cybersecurity quizzes (Levels 1-3 complete!)")
        print(f"Total questions added: {len(level_1_questions) + len(level_2_questions) + len(level_3_questions)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_cybersecurity_quizzes()
