#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# Sentinel-Link / FlowLens — VPS Deployment Script
# ═══════════════════════════════════════════════════════════════
#
# Prerequisites on VPS:
#   sudo apt update && sudo apt install -y docker.io docker-compose-plugin certbot python3-certbot-nginx
#   sudo usermod -aG docker $USER
#
# DNS Records (all pointing to VPS IP):
#   hackathon.lynqcr.com  → A record
#   analytics.lynqcr.com  → A record
#   bancoa.lynqcr.com     → A record
#   bancob.lynqcr.com     → A record
#   bancoc.lynqcr.com     → A record
#   finsta.lynqcr.com     → A record
#   safecall.lynqcr.com   → A record
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh           # Build and start all services
#   ./deploy.sh ssl       # After services are up, install SSL certs
#   ./deploy.sh seed      # Seed databases with demo data
#   ./deploy.sh logs      # Tail all logs
#   ./deploy.sh down      # Stop everything
# ═══════════════════════════════════════════════════════════════

COMPOSE="docker compose -f docker-compose.prod.yml"
DOMAINS=(
    hackathon.lynqcr.com
    analytics.lynqcr.com
    bancoa.lynqcr.com
    bancob.lynqcr.com
    bancoc.lynqcr.com
    finsta.lynqcr.com
    safecall.lynqcr.com
)

case "${1:-up}" in

  up)
    echo "══════════════════════════════════════════"
    echo "  Sentinel-Link — Starting Production"
    echo "══════════════════════════════════════════"

    # Ensure .env exists
    if [ ! -f .env ]; then
        echo "ERROR: .env file not found. Copy .env.example and fill in values."
        exit 1
    fi

    # Build and start
    $COMPOSE up -d --build

    echo ""
    echo "Services are starting. Check status:"
    echo "  $COMPOSE ps"
    echo ""
    echo "Next steps:"
    echo "  1. Verify DNS records point to this server"
    echo "  2. Run './deploy.sh ssl' to install SSL certificates"
    echo "  3. Run './deploy.sh seed' to populate demo data"
    echo ""
    echo "URLs (HTTP until SSL is configured):"
    for d in "${DOMAINS[@]}"; do
        echo "  http://$d"
    done
    ;;

  ssl)
    echo "══════════════════════════════════════════"
    echo "  Installing SSL Certificates (Let's Encrypt)"
    echo "══════════════════════════════════════════"

    # Build certbot domain args
    DOMAIN_ARGS=""
    for d in "${DOMAINS[@]}"; do
        DOMAIN_ARGS="$DOMAIN_ARGS -d $d"
    done

    # Get certificates
    docker compose -f docker-compose.prod.yml exec -T nginx sh -c "apk add --no-cache certbot py3-certbot-nginx" || true

    # Run certbot from the host (needs access to nginx config)
    $COMPOSE run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email ottodev.1604@gmail.com \
        --agree-tos \
        --no-eff-email \
        $DOMAIN_ARGS

    # Generate SSL nginx config
    cat > nginx/ssl.conf << 'SSLEOF'
# SSL settings (included by each server block after certbot)
ssl_certificate     /etc/letsencrypt/live/hackathon.lynqcr.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/hackathon.lynqcr.com/privkey.pem;
ssl_protocols       TLSv1.2 TLSv1.3;
ssl_ciphers         HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache   shared:SSL:10m;
ssl_session_timeout 10m;
SSLEOF

    # Add SSL listener and redirect to each server block
    python3 - << 'PYEOF'
import re

with open("nginx/prod.conf", "r") as f:
    conf = f.read()

# For each server block with a server_name (not default), add SSL listener
domains = [
    "hackathon.lynqcr.com",
    "bancoa.lynqcr.com",
    "bancob.lynqcr.com",
    "bancoc.lynqcr.com",
    "analytics.lynqcr.com",
    "finsta.lynqcr.com",
    "safecall.lynqcr.com",
]

for domain in domains:
    # Add listen 443 ssl after listen 80 for each domain
    pattern = f"(    listen 80;\n    server_name {domain};)"
    replacement = f"""    listen 80;
    listen 443 ssl;
    server_name {domain};

    ssl_certificate     /etc/letsencrypt/live/hackathon.lynqcr.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hackathon.lynqcr.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;"""

    conf = conf.replace(
        f"    listen 80;\n    server_name {domain};",
        replacement
    )

with open("nginx/prod.conf", "w") as f:
    f.write(conf)

print("SSL directives added to nginx/prod.conf")
PYEOF

    # Reload nginx
    $COMPOSE exec nginx nginx -s reload

    echo ""
    echo "SSL installed! All sites now available via HTTPS:"
    for d in "${DOMAINS[@]}"; do
        echo "  https://$d"
    done
    ;;

  seed)
    echo "══════════════════════════════════════════"
    echo "  Seeding Databases"
    echo "══════════════════════════════════════════"

    echo "Waiting for services to be healthy..."
    sleep 5

    echo "Seeding Banco A..."
    $COMPOSE exec -T api_banco_a python -m banco_a.seed 2>/dev/null || echo "  (seed script not found or already seeded)"

    echo "Seeding Banco B..."
    $COMPOSE exec -T api_banco_b python -m banco_b.seed 2>/dev/null || echo "  (seed script not found or already seeded)"

    echo "Seeding Banco C..."
    $COMPOSE exec -T api_banco_c python -m banco_c.seed 2>/dev/null || echo "  (seed script not found or already seeded)"

    echo "Seeding Finsta..."
    $COMPOSE exec -T api_finsta python -m finsta.seed_finsta 2>/dev/null || echo "  (seed script not found or already seeded)"

    echo "Seeding SafeCall..."
    $COMPOSE exec -T api_safecall python -m safecall.seed_safecall 2>/dev/null || echo "  (seed script not found or already seeded)"

    echo "Seeding FlowLens Analytics (full intelligence data)..."
    $COMPOSE exec -T api_analytics python /app/seed_analytics_full.py 2>/dev/null || echo "  (analytics seed failed)"

    echo "Generating Resolved Case (Gemini correlation)..."
    $COMPOSE exec -T api_analytics python /app/seed_resolved_case.py 2>/dev/null || echo "  (resolved case generation failed)"

    echo ""
    echo "Seeding complete."
    echo "Access the evidence dossier at:"
    echo "  https://analytics.lynqcr.com/reports/cases/1/evidence.pdf"
    ;;

  logs)
    $COMPOSE logs -f --tail=50
    ;;

  down)
    echo "Stopping all services..."
    $COMPOSE down
    echo "Done. Data preserved in volumes."
    echo "To remove volumes too: $COMPOSE down -v"
    ;;

  restart)
    echo "Restarting all services..."
    $COMPOSE restart
    $COMPOSE exec nginx nginx -s reload
    ;;

  status)
    $COMPOSE ps
    ;;

  *)
    echo "Usage: ./deploy.sh [up|ssl|seed|logs|down|restart|status]"
    exit 1
    ;;

esac
