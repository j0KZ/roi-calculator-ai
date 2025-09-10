# ROI Calculator Installation Guide - Version 3.0

## Overview

This guide provides comprehensive installation instructions for ROI Calculator Version 3.0. The application has been significantly enhanced with multi-currency support, AI optimization, and professional document generation capabilities.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS, or Windows 10+
- **Python**: 3.8 or higher (3.10+ recommended)
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Storage**: 2 GB free space minimum
- **Network**: Internet connection for currency/tax data APIs

### Recommended Requirements
- **Operating System**: Ubuntu 20.04+, macOS 11+, or Windows 11
- **Python**: 3.10 or higher
- **Memory**: 8 GB RAM or more
- **Storage**: 5 GB free space
- **CPU**: 2+ cores for optimal performance
- **Network**: Stable internet for real-time features

### Database Requirements
- **Development**: SQLite (included)
- **Production**: PostgreSQL 12+ (recommended)

## Installation Methods

### Method 1: Quick Start (Recommended for Testing)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/roi-calculator.git
   cd roi-calculator
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Initialize Database**
   ```bash
   python setup_database.py
   ```

6. **Run Application**
   ```bash
   python src/web_interface.py
   ```

7. **Access Application**
   - Open browser to `http://localhost:8000`

### Method 2: Production Installation with PostgreSQL

#### Step 1: System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx
sudo apt install python3-dev libpq-dev build-essential
```

**CentOS/RHEL:**
```bash
sudo yum update
sudo yum install python3-pip python3-venv postgresql postgresql-server nginx
sudo yum install python3-devel postgresql-devel gcc
```

**macOS with Homebrew:**
```bash
brew install python postgresql nginx
```

#### Step 2: Database Setup

1. **Install and Start PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # CentOS/RHEL
   sudo postgresql-setup initdb
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # macOS
   brew services start postgresql
   ```

2. **Create Database and User**
   ```bash
   sudo -u postgres psql
   ```
   
   In PostgreSQL shell:
   ```sql
   CREATE DATABASE roi_calculator;
   CREATE USER roi_user WITH ENCRYPTED PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE roi_calculator TO roi_user;
   \q
   ```

#### Step 3: Application Setup

1. **Create Application User**
   ```bash
   sudo useradd -m -s /bin/bash roicalc
   sudo su - roicalc
   ```

2. **Clone and Setup Application**
   ```bash
   git clone https://github.com/yourusername/roi-calculator.git
   cd roi-calculator
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

   **Production .env Configuration:**
   ```bash
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=production
   PORT=8000
   
   # Database Configuration
   DATABASE_URL=postgresql://roi_user:your_secure_password@localhost/roi_calculator
   
   # Multi-Currency Configuration
   DEFAULT_CURRENCY=USD
   EXCHANGE_RATE_API_KEY=your-exchange-rate-api-key
   
   # Tax Configuration
   DEFAULT_TAX_JURISDICTION=US
   DEFAULT_TAX_REGION=
   IVA_RATE=0.19
   
   # Analytics Configuration
   MONTE_CARLO_ITERATIONS=1000
   SENSITIVITY_RANGE=0.5
   
   # AI Optimization
   OPTIMIZATION_INDUSTRY=ecommerce
   BENCHMARK_DATA_SOURCE=internal
   
   # Document Generation
   DOCUMENT_TEMPLATE_DIR=templates
   CHART_GENERATION_DPI=300
   
   # Security
   TRUSTED_HOSTS=your-domain.com
   MAX_CONTENT_LENGTH=16777216  # 16MB
   ```

4. **Initialize Database**
   ```bash
   python setup_database.py
   ```

5. **Test Installation**
   ```bash
   python src/web_interface.py
   ```

#### Step 4: Production Deployment with Gunicorn

1. **Create Gunicorn Configuration**
   ```bash
   nano gunicorn_config.py
   ```
   
   ```python
   bind = "127.0.0.1:8000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 120
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   user = "roicalc"
   group = "roicalc"
   daemon = False
   pidfile = "/var/run/roi-calculator.pid"
   accesslog = "/var/log/roi-calculator/access.log"
   errorlog = "/var/log/roi-calculator/error.log"
   loglevel = "info"
   ```

2. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/roi-calculator.service
   ```
   
   ```ini
   [Unit]
   Description=ROI Calculator Web Application
   After=network.target postgresql.service
   Requires=postgresql.service
   
   [Service]
   Type=simple
   User=roicalc
   Group=roicalc
   WorkingDirectory=/home/roicalc/roi-calculator
   Environment=PATH=/home/roicalc/roi-calculator/venv/bin
   ExecStart=/home/roicalc/roi-calculator/venv/bin/gunicorn --config gunicorn_config.py src.web_interface:app
   ExecReload=/bin/kill -s HUP $MAINPID
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Create Log Directories**
   ```bash
   sudo mkdir -p /var/log/roi-calculator
   sudo chown roicalc:roicalc /var/log/roi-calculator
   ```

4. **Start and Enable Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start roi-calculator
   sudo systemctl enable roi-calculator
   sudo systemctl status roi-calculator
   ```

#### Step 5: Nginx Reverse Proxy Setup

1. **Create Nginx Configuration**
   ```bash
   sudo nano /etc/nginx/sites-available/roi-calculator
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       
       client_max_body_size 16M;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 120s;
           proxy_connect_timeout 10s;
           proxy_send_timeout 120s;
       }
       
       location /static/ {
           alias /home/roicalc/roi-calculator/static/;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
       
       location /download/ {
           alias /home/roicalc/roi-calculator/reports/;
           expires 1h;
           add_header X-Robots-Tag "noindex, nofollow";
       }
   }
   ```

2. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/roi-calculator /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Method 3: Docker Installation (Recommended for Development)

1. **Prerequisites**
   - Docker and Docker Compose installed

2. **Create Docker Compose File**
   ```yaml
   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://roi_user:roi_password@db:5432/roi_calculator
         - FLASK_ENV=development
       depends_on:
         - db
       volumes:
         - ./reports:/app/reports
         - ./proposals:/app/proposals
   
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=roi_calculator
         - POSTGRES_USER=roi_user
         - POSTGRES_PASSWORD=roi_password
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
   
   volumes:
     postgres_data:
   ```

3. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       postgresql-client \
       build-essential \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Create output directories
   RUN mkdir -p reports proposals presentations
   
   # Expose port
   EXPOSE 8000
   
   # Run application
   CMD ["python", "src/web_interface.py"]
   ```

4. **Start Application**
   ```bash
   docker-compose up -d
   ```

## Configuration

### Environment Variables

#### Required Variables
- `SECRET_KEY`: Flask secret key for security
- `DATABASE_URL`: Database connection string

#### Optional Variables
- `EXCHANGE_RATE_API_KEY`: For real-time currency rates
- `DEFAULT_CURRENCY`: Default currency (USD, EUR, CLP, etc.)
- `DEFAULT_TAX_JURISDICTION`: Default tax region
- `OPTIMIZATION_INDUSTRY`: Industry for benchmarking

### External API Configuration

#### Exchange Rate API Setup
1. Sign up at https://exchangerate-api.com/
2. Get your free API key
3. Add to .env: `EXCHANGE_RATE_API_KEY=your_key_here`

#### Document Storage Configuration
For production, configure cloud storage:
```bash
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=roi-calculator-documents

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT=your_project
GOOGLE_CLOUD_BUCKET=roi-calculator-documents
```

## Verification

### Health Check
```bash
curl http://localhost:8000/health
```

### Feature Testing
1. **Currency Conversion**: Test with different currencies
2. **Tax Calculation**: Verify tax calculations for your region
3. **Document Generation**: Generate a test proposal
4. **AI Optimization**: Run cost optimization analysis
5. **Template Management**: Create and use templates

### Performance Testing
```bash
# Install testing tools
pip install locust

# Run performance tests
locust -f tests/performance_test.py --host=http://localhost:8000
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Solution: Ensure all dependencies are installed
pip install -r requirements.txt --force-reinstall
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U roi_user -d roi_calculator
```

#### Currency API Errors
- Verify API key is correct
- Check internet connectivity
- Fallback rates will be used if API fails

#### Memory Issues with Document Generation
```bash
# Increase memory limits in .env
MAX_CONTENT_LENGTH=33554432  # 32MB
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R roicalc:roicalc /home/roicalc/roi-calculator
chmod +x src/web_interface.py
```

### Log Analysis
```bash
# Application logs
tail -f /var/log/roi-calculator/error.log

# System logs
journalctl -u roi-calculator -f

# Nginx logs
tail -f /var/log/nginx/error.log
```

## Maintenance

### Backup Procedures
```bash
# Database backup
pg_dump -h localhost -U roi_user roi_calculator > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /home/roicalc/roi-calculator
```

### Update Procedures
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations (if any)
python migrate_database.py

# Restart service
sudo systemctl restart roi-calculator
```

### Monitoring
- Set up monitoring for disk space (documents can accumulate)
- Monitor database size and performance
- Track API usage if using external services
- Monitor memory usage during batch operations

## Security Considerations

### Production Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable PostgreSQL SSL
- [ ] Configure HTTPS with SSL certificate
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Implement rate limiting
- [ ] Regular backup verification

### SSL Certificate Setup (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Support

### Getting Help
- **Documentation**: Check docs/ directory
- **Issues**: Report on GitHub Issues
- **Email**: support@roi-calculator.com

### Performance Tuning
- Increase worker processes for high traffic
- Configure Redis for caching (optional)
- Optimize PostgreSQL settings
- Use CDN for static assets

---

*Installation Guide for ROI Calculator Version 3.0*
*Last updated: December 2024*