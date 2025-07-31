#!/bin/bash

# Production Deployment Script for Shipping GUI
# Usage: ./scripts/deploy.sh [environment] [version]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"
REGISTRY="${DOCKER_REGISTRY:-ghcr.io/your-username}"
IMAGE_NAME="${REGISTRY}/shipping-gui"
COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [[ ! -f "$PROJECT_ROOT/.env.${ENVIRONMENT}" ]]; then
        log_error "Environment file .env.${ENVIRONMENT} not found"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Build and push Docker image
build_and_push() {
    log_info "Building Docker image..."
    
    cd "$PROJECT_ROOT"
    
    # Build image
    docker build -f Dockerfile.production -t "${IMAGE_NAME}:${VERSION}" .
    docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
    
    # Push to registry
    log_info "Pushing image to registry..."
    docker push "${IMAGE_NAME}:${VERSION}"
    docker push "${IMAGE_NAME}:latest"
    
    log_info "Image built and pushed successfully"
}

# Deploy using Docker Compose
deploy_compose() {
    log_info "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    # Load environment variables
    export $(cat ".env.${ENVIRONMENT}" | grep -v '^#' | xargs)
    export IMAGE_TAG="${VERSION}"
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Deploy with zero downtime
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    
    # Wait for health checks
    log_info "Waiting for application to be healthy..."
    wait_for_health
    
    log_info "Deployment completed successfully"
}

# Deploy to Kubernetes
deploy_k8s() {
    log_info "Deploying to Kubernetes..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    # Note: Secrets should be created separately for security
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/redis.yaml
    
    # Update image version
    kubectl set image deployment/shipping-gui-app shipping-gui="${IMAGE_NAME}:${VERSION}" -n shipping-gui
    
    # Wait for rollout
    kubectl rollout status deployment/shipping-gui-app -n shipping-gui --timeout=300s
    
    log_info "Kubernetes deployment completed successfully"
}

# Wait for application health
wait_for_health() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:5000/health > /dev/null; then
            log_info "Application is healthy"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, retrying in 10s..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Application failed to become healthy"
    return 1
}

# Rollback function
rollback() {
    local previous_version="${1:-}"
    
    if [[ -z "$previous_version" ]]; then
        log_error "Previous version not specified for rollback"
        exit 1
    fi
    
    log_warn "Rolling back to version: $previous_version"
    
    if [[ "$ENVIRONMENT" == "k8s" ]]; then
        kubectl set image deployment/shipping-gui-app shipping-gui="${IMAGE_NAME}:${previous_version}" -n shipping-gui
        kubectl rollout status deployment/shipping-gui-app -n shipping-gui --timeout=300s
    else
        export IMAGE_TAG="$previous_version"
        docker-compose -f "$COMPOSE_FILE" up -d
        wait_for_health
    fi
    
    log_info "Rollback completed successfully"
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old images..."
    
    # Remove old local images (keep last 3)
    docker images "${IMAGE_NAME}" --format "table {{.Tag}}" | tail -n +4 | head -n -3 | \
    xargs -I {} docker rmi "${IMAGE_NAME}:{}" || true
    
    # Cleanup unused volumes and networks
    docker system prune -f --volumes
    
    log_info "Cleanup completed"
}

# Main deployment logic
main() {
    log_info "Starting deployment for environment: $ENVIRONMENT, version: $VERSION"
    
    case "$1" in
        "check")
            check_prerequisites
            ;;
        "build")
            check_prerequisites
            build_and_push
            ;;
        "deploy")
            check_prerequisites
            build_and_push
            if [[ "$ENVIRONMENT" == "k8s" ]]; then
                deploy_k8s
            else
                deploy_compose
            fi
            ;;
        "rollback")
            rollback "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            log_info "Usage: $0 {check|build|deploy|rollback|cleanup} [version]"
            log_info "Environment: $ENVIRONMENT"
            log_info "Available commands:"
            log_info "  check    - Check prerequisites only"
            log_info "  build    - Build and push Docker image"
            log_info "  deploy   - Full deployment (build + deploy)"
            log_info "  rollback - Rollback to previous version"
            log_info "  cleanup  - Clean up old images"
            exit 1
            ;;
    esac
}

# Handle script arguments
if [[ $# -eq 0 ]]; then
    main "deploy"
else
    main "$@"
fi