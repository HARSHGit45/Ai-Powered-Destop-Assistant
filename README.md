# AI-Powered Desktop Assistant 🤖

A comprehensive desktop control system developed for the Blue BIT Hackathon by MLSC Student Chapter that allows natural language control of system settings and file operations.

## Team Members 👥

- Anushka Patil
- Anjali Auti
- Ankush Anne

## Features ✨

- **System Controls**
  - Brightness adjustment
  - Volume control
  - Battery status monitoring
  - WiFi management
  - Bluetooth device control

- **File Operations**
  - Secure file management
  - Protected system file access
  - Directory navigation
  - File search capabilities
  - Authentication for sensitive operations

## Installation 🚀

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Ai-Powered-Desktop-Assistant.git
   cd Ai-Powered-Desktop-Assistant
   ```

2. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   - Create a `.env` file in the root directory
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

## Usage 💡

1. **Start the Frontend**
   ```bash
   npm run dev
   ```

2. **Start the Backend**
   ```bash
   python system_controls/main.py
   ```

### Available Commands:

- **System Controls:**
  - "what's the brightness?"
  - "make it louder"
  - "dim the screen"
  - "show wifi networks"
  - "turn bluetooth on/off"
  - "get battery status"

- **File Operations:**
  - List directories
  - Create/delete files
  - Move/copy files
  - Search for files
  - Access system files (with authentication)

## Security Features 🔒

- Automatic privilege escalation for sensitive operations
- Protected system file access
- Authentication for critical file operations
- Secure handling of system modifications

## Dependencies 📦

### Frontend
- React
- Next.js
- Other frontend packages (installed via npm)

### Backend
- screen-brightness-control
- pycaw
- psutil
- pywifi
- bleak
- groq
- python-dotenv
- pywin32

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments 👏

- MLSC Student Chapter
- Blue BIT Hackathon organizers
- All contributors and testers

## Contact 📧

Project Link: [https://github.com/harshgit45/Ai-Powered-Desktop-Assistant](https://github.com/harshgit45/Ai-Powered-Desktop-Assistant)
