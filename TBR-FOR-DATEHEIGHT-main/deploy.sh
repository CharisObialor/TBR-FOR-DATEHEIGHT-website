#!/bin/bash
# Blue-Green Deployment Script for TBR Solutions
# Usage: ./deploy.sh <blue|green|switch|rollback>

set -euo pipefail

DEPLOY_DIR="/opt/tbr"
ACTIVE_FILE="${DEPLOY_DIR}/.active"
COMPOSE_FILE="${DEPLOY_DIR}/docker-compose.yml"
BACKUP_DIR="${DEPLOY_DIR}/backups"

mkdir -p "${BACKUP_DIR}"

get_active() {
    if [ -f "$ACTIVE_FILE" ]; then
        cat "$ACTIVE_FILE"
    else
        echo "blue"
    fi
}

get_inactive() {
    local active=$(get_active)
    if [ "$active" = "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

switch_traffic() {
    local target=$1
    echo "Switching traffic to ${target}..."

    # Update active deployment
    echo "$target" > "$ACTIVE_FILE"

    # Update nginx config to point to the new backend
    local upstream_name="backend_${target}"
    sed -i "s/proxy_pass http:\/\/backend_[a-z]*/proxy_pass http:\/\/${upstream_name}/g" \
        "${DEPLOY_DIR}/nginx/nginx.conf"

    # Reload nginx
    docker-compose -f "$COMPOSE_FILE" exec frontend nginx -s reload

    echo "Traffic switched to ${target}. Previous deployment is still running."
}

deploy() {
    local target=$1
    echo "Deploying to ${target}..."

    # Tag the backend image with the target
    docker-compose -f "$COMPOSE_FILE" build "backend-${target}"

    # Start the new deployment
    docker-compose -f "$COMPOSE_FILE" up -d "backend-${target}"

    # Wait for health check
    echo "Waiting for ${target} to pass health check..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" exec "backend-${target}" \
            curl -sf http://localhost:8000/api/ > /dev/null 2>&1; then
            echo "${target} is healthy!"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "Health check failed for ${target}. Rolling back..."
            docker-compose -f "$COMPOSE_FILE" stop "backend-${target}"
            exit 1
        fi
        sleep 2
    done

    # Backup current active state
    local active=$(get_active)
    cp "$ACTIVE_FILE" "${BACKUP_DIR}/pre-deploy-$(date +%Y%m%d-%H%M%S)"

    # Switch traffic to the new deployment
    switch_traffic "$target"

    echo "Deployment to ${target} complete!"
}

case "${1:-}" in
    blue)
        deploy "blue"
        ;;
    green)
        deploy "green"
        ;;
    switch)
        local inactive=$(get_inactive)
        switch_traffic "$inactive"
        ;;
    rollback)
        local latest_backup=$(ls -t "${BACKUP_DIR}/pre-deploy-"* 2>/dev/null | head -1)
        if [ -z "$latest_backup" ]; then
            echo "No backup found for rollback."
            exit 1
        fi
        local previous=$(cat "$latest_backup")
        switch_traffic "$previous"
        echo "Rolled back to ${previous}"
        ;;
    status)
        echo "Active deployment: $(get_active)"
        echo "Inactive deployment: $(get_inactive)"
        echo ""
        echo "Running containers:"
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    *)
        echo "Usage: $0 {blue|green|switch|rollback|status}"
        echo ""
        echo "Commands:"
        echo "  blue      Deploy to blue environment"
        echo "  green     Deploy to green environment"
        echo "  switch    Switch traffic to the inactive environment"
        echo "  rollback  Rollback to the previous deployment"
        echo "  status    Show current deployment status"
        exit 1
        ;;
esac
