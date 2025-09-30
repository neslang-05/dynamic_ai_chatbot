#!/usr/bin/env powershell

# Docker Compose Startup Script for Dynamic AI Chatbot
# This script provides easy commands to manage the entire project with Docker
# Fixed PSScriptAnalyzer warnings: removed unused variables and used approved verbs

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "build", "logs", "status", "clean", "dev", "prod", "help")]
    [string]$Command = "help",
    
    [switch]$Detached,
    [switch]$Build,
    [switch]$Follow
)

# Configuration
$EnvFile = ".env.docker"

# Colors for output
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    try {
        Write-Host $Text -ForegroundColor $Color
    } catch {
        # Fallback to plain text if color fails
        Write-Host $Text
    }
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-ColorText "=> $Text" "Cyan"
    Write-ColorText ("=" * 50) "Cyan"
}

function Write-Success {
    param([string]$Text)
    Write-ColorText "[OK] $Text" "Green"
}

function Write-Warning {
    param([string]$Text)
    Write-ColorText "[WARNING] $Text" "Yellow"
}

function Write-Error {
    param([string]$Text)
    Write-ColorText "[ERROR] $Text" "Red"
}

function Show-Help {
    Write-Header "Dynamic AI Chatbot - Docker Management"
    Write-Host ""
    Write-ColorText "USAGE:" "Yellow"
    Write-Host "  .\docker-run.ps1 <command> [options]"
    Write-Host ""
    Write-ColorText "COMMANDS:" "Yellow"
    Write-Host "  start     - Start all services"
    Write-Host "  stop      - Stop all services"
    Write-Host "  restart   - Restart all services"
    Write-Host "  build     - Build all Docker images"
    Write-Host "  logs      - Show service logs"
    Write-Host "  status    - Show service status"
    Write-Host "  clean     - Clean up containers and volumes"
    Write-Host "  dev       - Start in development mode"
    Write-Host "  prod      - Start in production mode with Nginx"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-ColorText "OPTIONS:" "Yellow"
    Write-Host "  -Detached - Run in background (for start command)"
    Write-Host "  -Build    - Force rebuild images"
    Write-Host "  -Follow   - Follow logs in real-time"
    Write-Host ""
    Write-ColorText "EXAMPLES:" "Yellow"
    Write-Host "  .\docker-run.ps1 start -Detached"
    Write-Host "  .\docker-run.ps1 build"
    Write-Host "  .\docker-run.ps1 logs -Follow"
    Write-Host "  .\docker-run.ps1 dev"
    Write-Host ""
}

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "Docker: $dockerVersion"
    } catch {
        Write-Error "Docker is not installed or not running"
        return $false
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose: $composeVersion"
    } catch {
        Write-Error "Docker Compose is not installed"
        return $false
    }
    
    # Check if environment file exists
    if (!(Test-Path $EnvFile)) {
        Write-Warning "Environment file $EnvFile not found"
        Write-Host "Creating from template..."
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" $EnvFile
            Write-Success "Created $EnvFile from template"
        } else {
            Write-Warning "Please create $EnvFile manually"
        }
    }
    
    return $true
}

function Start-Services {
    param([bool]$IsDev = $false, [bool]$IsProd = $false)
    
    Write-Header "Starting Dynamic AI Chatbot Services"
    
    $composeArgs = @("up")
    
    if ($Detached) {
        $composeArgs += "-d"
    }
    
    if ($Build) {
        $composeArgs += "--build"
    }
    
    if ($IsProd) {
        $composeArgs += "--profile", "production"
    }
    
    Write-Host "Command: docker-compose $($composeArgs -join ' ')"
    
    try {
        docker-compose @composeArgs
        
        if ($Detached) {
            Write-Success "Services started in background"
            Show-ServiceStatus
            Show-AccessUrls
        }
    } catch {
        Write-Error "Failed to start services: $_"
    }
}

function Stop-Services {
    Write-Header "Stopping Dynamic AI Chatbot Services"
    
    try {
        docker-compose down
        Write-Success "All services stopped"
    } catch {
        Write-Error "Failed to stop services: $_"
    }
}

function Restart-Services {
    Write-Header "Restarting Dynamic AI Chatbot Services"
    
    Stop-Services
    Start-Sleep -Seconds 3
    Start-Services
}

function New-DockerImages {
    Write-Header "Creating Docker Images"
    
    try {
        docker-compose build --no-cache
        Write-Success "All images built successfully"
    } catch {
        Write-Error "Failed to build images: $_"
    }
}

function Show-Logs {
    Write-Header "Service Logs"
    
    $logArgs = @("logs")
    
    if ($Follow) {
        $logArgs += "-f"
    }
    
    try {
        docker-compose @logArgs
    } catch {
        Write-Error "Failed to show logs: $_"
    }
}

function Show-ServiceStatus {
    Write-Header "Service Status"
    
    try {
        docker-compose ps
    } catch {
        Write-Error "Failed to get service status: $_"
    }
}

function Remove-DockerEnvironment {
    Write-Header "Removing Docker Environment"
    
    Write-Warning "This will remove all containers, images, and volumes for this project"
    $confirm = Read-Host "Are you sure? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        try {
            docker-compose down -v --rmi all
            Write-Success "Environment cleaned"
        } catch {
            Write-Error "Failed to clean environment: $_"
        }
    } else {
        Write-Host "Cancelled"
    }
}

function Show-AccessUrls {
    Write-Header "Access URLs"
    
    Write-ColorText "Main Chatbot API:" "Green"
    Write-Host "   http://localhost:8000"
    Write-Host "   http://localhost:8000/docs (API Documentation)"
    Write-Host "   http://localhost:8000/static/chatbot_secure.html (Chat UI)"
    Write-Host ""
    
    Write-ColorText "Dashboard Backend:" "Blue"
    Write-Host "   http://localhost:5000"
    Write-Host "   http://localhost:5000/api/health"
    Write-Host ""
    
    Write-ColorText "Dashboard Frontend:" "Magenta"
    Write-Host "   http://localhost:3000"
    Write-Host ""
    
    Write-ColorText "Database Services:" "Yellow"
    Write-Host "   Redis: localhost:6379"
    Write-Host "   MongoDB: localhost:27017"
    Write-Host ""
    
    Write-ColorText "Production (with Nginx):" "Cyan"
    Write-Host "   http://localhost (Main application)"
    Write-Host "   http://localhost/dashboard (Dashboard)"
    Write-Host ""
}

# Main script logic
if (!(Test-Prerequisites)) {
    exit 1
}

switch ($Command) {
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "build" {
        New-DockerImages
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-ServiceStatus
        Show-AccessUrls
    }
    "clean" {
        Remove-DockerEnvironment
    }
    "dev" {
        Write-Header "Starting Development Environment"
        Start-Services -IsDev $true
    }
    "prod" {
        Write-Header "Starting Production Environment"
        Start-Services -IsProd $true
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}