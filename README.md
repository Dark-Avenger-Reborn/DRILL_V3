# 🎯 DRILL: Advanced C2 Framework v3.0

**DRILL** (Distributable Remote Integrated Lightweight Link) is a powerful and stealthy Command and Control (C2) framework designed for seamless operation across various environments.

## 🚀 Key Features

### 🌐 WebSocket Communication
DRILL utilizes WebSocket protocol for C2 communications, effectively bypassing firewalls and proxies. This allows for real-time, bidirectional communication between the agent and the server, enhancing stealth and efficiency.

### 🔌 Single Port Operation
All traffic flows through a single port using HTTP/HTTPS, simplifying network traversal and making it easier to disguise as legitimate traffic.

### ☁️ Cloudflare Tunnel Compatibility
DRILL can be easily tunneled through Cloudflare, providing an additional layer of security and obfuscation for C2 communications.

### 🐳 Cross-Platform Payload Generation
Built-in Docker integration enables seamless payload creation for both Linux, Windows and OSX targets, expanding the framework's versatility.

### 🔒 Robust Persistence Mechanisms
- **Windows**: Implements startup registry keys and PowerShell profile modifications (Powershell profile is temporarily disabled due to a bug)
- **Linux**: Creates a user-local systemd process for persistent access
- **OSX**: Uses launch agents to run itself on startup


### 📂 Advanced File Transfer Capabilities
- Send and receive files to/from single or multiple machines simultaneously
- Supports transfer of executable files, enhancing post-exploitation flexibility

### 🛠️ Post-Exploitation Modules (PEM)
- Credential theft tools for harvesting login information
- Mass command execution across multiple compromised systems
- Easily expandable module system for future enhancements

### 🎨 Redesigned User Interface
Version 3.0 features a completely overhauled UI, improving usability and efficiency for operators.

## 🏗️ Architecture

DRILL follows a typical C2 framework architecture:

1. **Agent**: Malware running on targeted systems, connecting back to the teamserver
2. **Teamserver**: Central backend service managing agent communications and operator interactions
3. **Client**: Web interface for operators to control the teamserver and issue commands

## 🔮 Upcoming Features

- Enhanced post-exploitation modules
- Remote Desktop Protocol (RDP) mode:
  - Keyboard and mouse locking
  - Input mirroring from operator to target
  - Target screen viewing
  - Webcam access

## 📥 Installation

```bash
# Clone the repo
git clone https://github.com/redteam-malware/DRILL_V3.git

# Run the installer, avoid running it as root
cd DRILL_V3
bash ./install.sh
```

## 🖥️ Usage

```bash
# Basic usage example
python3 main.py
```

## ⚠️ Security Considerations

> **Warning**: This tool is intended for authorized penetration testing and red team operations only. Misuse of this software may be illegal in your jurisdiction. Use responsibly and ethically.

<!-- ## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information. -->

## 📜 License

Apache-2.0 license

## ❗ Disclaimer

This project is for educational and authorized testing purposes only. The authors are not responsible for any misuse or damage caused by this software.

---

<details>
<summary>📊 Project Stats</summary>

## Star History

<a href="https://star-history.com/#Dark-Avenger-Reborn/DRILL_V3&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Dark-Avenger-Reborn/DRILL_V3&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Dark-Avenger-Reborn/DRILL_V3&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Dark-Avenger-Reborn/DRILL_V3&type=Date" />
 </picture>
</a>

</details>
