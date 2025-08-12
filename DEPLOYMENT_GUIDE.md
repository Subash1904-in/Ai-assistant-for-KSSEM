# KSSEM Virtual AI Assistant - Deployment Guide

## 🚀 Quick Start Deployment

### Option 1: Complete System (Recommended)
```bash
# Clone and setup
git clone <repository-url>
cd kssem-virtual-assistant

# Install dependencies
pip install -r requirements.txt

# Start the complete system
python main.py
```

### Option 2: API Only
```bash
# Start API server only
python main.py --mode api --port 8000
```

### Option 3: GUI Only (requires API running separately)
```bash
# Start GUI interface only
python main.py --mode gui
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, Windows, or macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

### Hardware Requirements (Kiosk)
- **Display**: 15" touchscreen minimum (1200x800 resolution)
- **CPU**: Dual-core 2.0GHz or higher
- **RAM**: 8GB recommended for smooth operation
- **Storage**: SSD preferred for faster startup

## 🔧 Installation Steps

### 1. Environment Setup

#### Linux/Ubuntu
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install system dependencies for GUI
sudo apt install python3-tk python3-dev libffi-dev -y
```

#### Windows
```powershell
# Install Python 3.8+ from python.org
# Install Git from git-scm.com
# Ensure pip is available
```

#### macOS
```bash
# Install Python using Homebrew
brew install python3 git

# Install tkinter if needed
brew install python-tk
```

### 2. Project Setup

```bash
# Clone repository
git clone <repository-url>
cd kssem-virtual-assistant

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Configuration

```bash
# Copy and customize configuration
cp config/kssem_config.json config/kssem_config_local.json

# Edit configuration for your environment
nano config/kssem_config_local.json
```

### 4. Data Validation

```bash
# Run integration test
python3 -c "
import sys, os, json
sys.path.insert(0, 'src')

# Test data loading
with open('data/knowledge_base/faq.json') as f:
    faq = json.load(f)
print(f'✓ {len(faq[\"frequently_asked_questions\"])} FAQ entries loaded')

with open('data/kssem_campus_map/landmarks.json') as f:
    map_data = json.load(f)
print(f'✓ {len(map_data[\"buildings\"])} buildings mapped')

print('✅ Data validation complete')
"
```

## 🖥️ Production Deployment

### Kiosk Mode Setup

#### 1. Auto-start Configuration

**Linux (systemd service)**
```bash
# Create service file
sudo nano /etc/systemd/system/kssem-assistant.service
```

```ini
[Unit]
Description=KSSEM Virtual AI Assistant
After=network.target

[Service]
Type=simple
User=kiosk
WorkingDirectory=/home/kiosk/kssem-virtual-assistant
Environment=PATH=/home/kiosk/kssem-virtual-assistant/venv/bin
ExecStart=/home/kiosk/kssem-virtual-assistant/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable kssem-assistant.service
sudo systemctl start kssem-assistant.service
```

#### 2. Kiosk Mode (Full Screen)

**Linux Desktop Environment**
```bash
# Create kiosk startup script
nano /home/kiosk/start_kiosk.sh
```

```bash
#!/bin/bash
# Disable screen saver
xset s off
xset -dpms
xset s noblank

# Start KSSEM Assistant in fullscreen
cd /home/kiosk/kssem-virtual-assistant
python main.py --mode full

# Re-enable on exit
xset s on
xset +dpms
```

```bash
# Make executable
chmod +x /home/kiosk/start_kiosk.sh

# Add to desktop autostart
mkdir -p ~/.config/autostart
nano ~/.config/autostart/kssem-kiosk.desktop
```

```ini
[Desktop Entry]
Type=Application
Name=KSSEM Kiosk
Exec=/home/kiosk/start_kiosk.sh
Hidden=false
X-GNOME-Autostart-enabled=true
```

### Network Configuration

#### 1. Static IP Setup (Recommended)
```bash
# Edit network configuration
sudo nano /etc/netplan/01-network-manager-all.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
# Apply configuration
sudo netplan apply
```

#### 2. Firewall Configuration
```bash
# Allow API port
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### Database Setup (Production)

#### SQLite (Default - No setup required)
The system uses file-based storage by default.

#### PostgreSQL (Recommended for production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE kssem_assistant;"
sudo -u postgres psql -c "CREATE USER kssem_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kssem_assistant TO kssem_user;"

# Update configuration
export DATABASE_URL="postgresql://kssem_user:secure_password@localhost/kssem_assistant"
```

## 🐳 Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src

# Start application
CMD ["python", "main.py", "--mode", "api"]
```

### 2. Build and Run
```bash
# Build Docker image
docker build -t kssem-assistant .

# Run container
docker run -d \
  --name kssem-assistant \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  kssem-assistant

# Check logs
docker logs kssem-assistant
```

### 3. Docker Compose (Full Stack)
```yaml
version: '3.8'

services:
  kssem-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - KSSEM_DEBUG=false
      - DATABASE_URL=postgresql://kssem_user:password@db:5432/kssem_assistant
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: kssem_assistant
      POSTGRES_USER: kssem_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Start with Docker Compose
docker-compose up -d
```

## 🔧 Configuration Management

### Environment Variables
```bash
# API Configuration
export KSSEM_API_HOST=0.0.0.0
export KSSEM_API_PORT=8000
export KSSEM_DEBUG=false

# Security
export KSSEM_ENCRYPTION_KEY=your-secret-key-here
export KSSEM_JWT_SECRET=jwt-secret-key

# Database
export DATABASE_URL=sqlite:///data/kssem.db

# Logging
export KSSEM_LOG_LEVEL=INFO
export KSSEM_LOG_FILE=/var/log/kssem/assistant.log
```

### Custom Configuration
```json
{
  "college_info": {
    "name": "Your Institution Name",
    "short_name": "YIN",
    "location": "Your City, State",
    "contact": {
      "phone": "+1-XXX-XXX-XXXX",
      "email": "info@yourinstitution.edu"
    }
  },
  "kiosk_settings": {
    "response_timeout": 2,
    "supported_languages": ["english"],
    "accessibility_features": {
      "voice_guidance": true,
      "high_contrast": true
    }
  }
}
```

## 📊 Monitoring and Maintenance

### 1. Health Monitoring
```bash
# Check API health
curl http://localhost:8000/health

# Check system resources
htop
df -h
free -m
```

### 2. Log Management
```bash
# View real-time logs
tail -f logs/kssem_assistant.log

# Rotate logs (add to crontab)
0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/kssem-assistant
```

### 3. Backup Strategy
```bash
# Backup data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Backup database (if using PostgreSQL)
pg_dump kssem_assistant > backup_$(date +%Y%m%d).sql
```

### 4. Updates and Maintenance
```bash
# Update system
git pull origin main
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart kssem-assistant
```

## 🔒 Security Considerations

### 1. Network Security
- Use HTTPS in production (add SSL certificates)
- Implement rate limiting
- Configure firewall rules
- Use VPN for remote access

### 2. Application Security
- Change default encryption keys
- Enable audit logging
- Regular security updates
- Input validation and sanitization

### 3. Data Privacy
- GDPR compliance enabled by default
- Regular data cleanup (30-day retention)
- Encrypted data storage
- Anonymized logging

## 🧪 Testing Deployment

### 1. API Testing
```bash
# Test health endpoint
curl -X GET http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Where is the library?"}'

# Test navigation endpoint
curl -X POST http://localhost:8000/navigation \
  -H "Content-Type: application/json" \
  -d '{"destination": "library"}'
```

### 2. GUI Testing
```bash
# Start GUI in test mode
python main.py --mode gui --debug

# Test accessibility features
# Test touch interactions
# Verify map display
```

### 3. Integration Testing
```bash
# Run full system test
python -m pytest tests/ -v

# Performance testing
ab -n 100 -c 10 http://localhost:8000/health
```

## 🆘 Troubleshooting

### Common Issues

#### 1. API Server Won't Start
```bash
# Check port availability
sudo netstat -tulpn | grep 8000

# Check permissions
ls -la main.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

#### 2. GUI Won't Launch
```bash
# Check display environment
echo $DISPLAY

# Test tkinter
python3 -c "import tkinter; print('Tkinter available')"

# Check X11 forwarding (if SSH)
ssh -X user@host
```

#### 3. Database Connection Issues
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U kssem_user -d kssem_assistant
```

#### 4. Memory Issues
```bash
# Check memory usage
free -m
ps aux --sort=-%mem | head

# Adjust Python memory limits
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Log Analysis
```bash
# Search for errors
grep -i error logs/kssem_assistant.log

# Check performance metrics
grep -i "performance_metric" logs/kssem_assistant.log

# Monitor API calls
grep -i "user_query" logs/kssem_assistant.log
```

## 📞 Support

### Getting Help
- **Documentation**: Check `/docs` directory
- **Logs**: Always include relevant log files
- **Configuration**: Verify all settings
- **Network**: Test connectivity

### Reporting Issues
1. Describe the problem clearly
2. Include system information
3. Provide error logs
4. List steps to reproduce
5. Mention expected vs actual behavior

---

**🎓 KSSEM Virtual AI Assistant Deployment Guide**  
*Version 1.0.0 - December 2024*