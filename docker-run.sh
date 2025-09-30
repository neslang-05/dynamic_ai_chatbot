#!/bin/bash

# Docker Compose Management Script for Dynamic AI Chatbot
# Unix/Linux/macOS version

set -e

# Configuration
PROJECT_NAME="dynamic-ai-chatbot"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}🚀 $1${NC}"
    echo -e "${CYAN}=================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    print_header "Dynamic AI Chatbot - Docker Management"
    echo ""
    echo -e "${YELLOW}USAGE:${NC}"
    echo "  ./docker-run.sh <command> [options]"
    echo ""
    echo -e "${YELLOW}COMMANDS:${NC}"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  build     - Build all Docker images"
    echo "  logs      - Show service logs"
    echo "  status    - Show service status"
    echo "  clean     - Clean up containers and volumes"
    echo "  dev       - Start in development mode"
    echo "  prod      - Start in production mode with Nginx"
    echo "  help      - Show this help message"
    echo ""
    echo -e "${YELLOW}OPTIONS:${NC}"
    echo "  -d        - Run in background (detached mode)"
    echo "  -b        - Force rebuild images"
    echo "  -f        - Follow logs in real-time"
    echo ""
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo "  ./docker-run.sh start -d"
    echo "  ./docker-run.sh build"
    echo "  ./docker-run.sh logs -f"
    echo "  ./docker-run.sh dev"
    echo ""
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker: $DOCKER_VERSION"
    else
        print_error "Docker is not installed or not running"
        return 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        print_success "Docker Compose: $COMPOSE_VERSION"
    else
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found"
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            print_success "Created $ENV_FILE from template"
        else
            print_warning "Please create $ENV_FILE manually"
        fi
    fi
    
    return 0
}

start_services() {
    local is_dev=$1
    local is_prod=$2
    local detached=$3
    local build=$4
    
    print_header "Starting Dynamic AI Chatbot Services"
    
    local compose_args="up"
    
    if [ "$detached" = true ]; then
        compose_args="$compose_args -d"
    fi
    
    if [ "$build" = true ]; then
        compose_args="$compose_args --build"
    fi
    
    if [ "$is_prod" = true ]; then
        compose_args="$compose_args --profile production"
    fi
    
    echo "Command: docker-compose $compose_args"
    
    if docker-compose $compose_args; then
        if [ "$detached" = true ]; then
            print_success "Services started in background"
            show_status
            show_access_urls
        fi
    else
        print_error "Failed to start services"
        return 1
    fi
}

stop_services() {
    print_header "Stopping Dynamic AI Chatbot Services"
    
    if docker-compose down; then
        print_success "All services stopped"
    else
        print_error "Failed to stop services"
        return 1
    fi
}

restart_services() {
    print_header "Restarting Dynamic AI Chatbot Services"
    
    stop_services
    sleep 3
    start_services false false true false
}

build_images() {
    print_header "Building Docker Images"
    
    if docker-compose build --no-cache; then
        print_success "All images built successfully"
    else
        print_error "Failed to build images"
        return 1
    fi
}

show_logs() {
    local follow=$1
    
    print_header "Service Logs"
    
    local log_args="logs"
    
    if [ "$follow" = true ]; then
        log_args="$log_args -f"
    fi
    
    docker-compose $log_args
}

show_status() {
    print_header "Service Status"
    docker-compose ps
}

clean_environment() {
    print_header "Cleaning Docker Environment"
    
    print_warning "This will remove all containers, images, and volumes for this project"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if docker-compose down -v --rmi all; then
            print_success "Environment cleaned"
        else
            print_error "Failed to clean environment"
            return 1
        fi
    else
        echo "Cancelled"
    fi
}

show_access_urls() {
    print_header "Access URLs"
    
    echo -e "${GREEN}🤖 Main Chatbot API:${NC}"
    echo "   http://localhost:8000"
    echo "   http://localhost:8000/docs (API Documentation)"
    echo "   http://localhost:8000/static/chatbot_secure.html (Chat UI)"
    echo ""
    
    echo -e "${BLUE}📊 Dashboard Backend:${NC}"
    echo "   http://localhost:5000"
    echo "   http://localhost:5000/api/health"
    echo ""
    
    echo -e "${CYAN}🎨 Dashboard Frontend:${NC}"
    echo "   http://localhost:3000"
    echo ""
    
    echo -e "${YELLOW}🗄️  Database Services:${NC}"
    echo "   Redis: localhost:6379"
    echo "   MongoDB: localhost:27017"
    echo ""
    
    echo -e "${CYAN}🌐 Production (with Nginx):${NC}"
    echo "   http://localhost (Main application)"
    echo "   http://localhost/dashboard (Dashboard)"
    echo ""
}

# Parse command line arguments
COMMAND="help"
DETACHED=false
BUILD=false
FOLLOW=false

while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|build|logs|status|clean|dev|prod|help)
            COMMAND=$1
            shift
            ;;
        -d|--detached)
            DETACHED=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check prerequisites
if ! check_prerequisites; then
    exit 1
fi

# Execute command
case $COMMAND in
    start)
        start_services false false $DETACHED $BUILD
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_images
        ;;
    logs)
        show_logs $FOLLOW
        ;;
    status)
        show_status
        show_access_urls
        ;;
    clean)
        clean_environment
        ;;
    dev)
        print_header "Starting Development Environment"
        start_services true false $DETACHED $BUILD
        ;;
    prod)
        print_header "Starting Production Environment"
        start_services false true $DETACHED $BUILD
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        ;;
esac