#!/bin/bash

# Twitter Hoax Detector - Quick Setup Script
# For Linux/macOS systems

echo "🚀 Twitter Hoax Detector - Quick Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python3 not found"
        return 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-dev python3-venv build-essential
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip python3-devel gcc
        else
            print_warning "Unknown Linux distribution - manual setup may be required"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install python3
        else
            print_warning "Homebrew not found - install from https://brew.sh/"
        fi
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated"
}

# Install Python dependencies
install_deps() {
    print_info "Installing Python dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install minimal requirements first
    if [ -f "requirements-minimal.txt" ]; then
        print_info "Installing minimal requirements..."
        pip install -r requirements-minimal.txt
        if [ $? -eq 0 ]; then
            print_status "Minimal requirements installed"
        else
            print_error "Failed to install minimal requirements"
            return 1
        fi
    fi
    
    # Try full requirements
    if [ -f "requirements.txt" ]; then
        print_info "Installing full requirements..."
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_status "Full requirements installed"
        else
            print_warning "Some full requirements failed - continuing with minimal setup"
        fi
    fi
}

# Create necessary directories
create_dirs() {
    print_info "Creating directories..."
    mkdir -p reports visualizations static templates logs
    mkdir -p app/services
    print_status "Directories created"
}

# Create config files
create_config() {
    print_info "Creating configuration files..."
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Twitter Hoax Detector Configuration
DEBUG=true
OPENAI_API_KEY=your-openai-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
USE_REAL_TWITTER_API=false
USE_REAL_BRAVE_API=false
EOF
        print_status ".env file created"
    else
        print_info ".env file already exists"
    fi
    
    # Create __init__.py files
    touch app/__init__.py
    touch app/services/__init__.py
}

# Test installation
test_install() {
    print_info "Testing installation..."
    
    python3 -c "
import sys
try:
    import fastapi
    import uvicorn
    import sqlalchemy
    print('✅ Core modules imported successfully')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Installation test passed"
        return 0
    else
        print_error "Installation test failed"
        return 1
    fi
}

# Show completion message
show_completion() {
    echo ""
    echo "🎉 Setup completed!"
    echo "=================="
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your API keys:"
    echo "   nano .env"
    echo ""
    echo "2. Activate virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Run the application:"
    echo "   python run.py both"
    echo ""
    echo "4. Access the dashboard:"
    echo "   http://localhost:8000"
    echo ""
    echo "📚 Documentation: README.md"
    echo "🐛 Issues: Check the logs/ directory"
}

# Main execution
main() {
    # Check Python
    if ! check_python; then
        print_error "Python check failed"
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create virtual environment
    create_venv
    
    # Activate virtual environment
    activate_venv
    
    # Install dependencies
    if ! install_deps; then
        print_error "Dependency installation failed"
        exit 1
    fi
    
    # Create directories and config
    create_dirs
    create_config
    
    # Test installation
    if test_install; then
        show_completion
    else
        print_warning "Setup completed with warnings - check installation"
    fi
}

# Run main function
main "$@" 