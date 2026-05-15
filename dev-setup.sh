#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Developer Setup Tool for Fresh Debian
# Extendable: just add entries to the TOOLS array below
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
log_info() { echo -e "${YELLOW}[+]${NC} $1"; }

# =============================================================================
# TOOL REGISTRY — Add your tools here
# Format: "key|Description|default(ON/OFF)|install_command(s)"
#
# Multi-line commands: separate with &&
# Use $HOME instead of ~ in commands
# =============================================================================

TOOLS=(
    "essentials|Build tools, git, curl, wget, htop, jq|ON|sudo apt-get update && sudo apt-get install -y build-essential git curl wget htop tree jq unzip zip ca-certificates gnupg lsb-release software-properties-common apt-transport-https net-tools dnsutils"

    "python|Python 3 + pip + venv|ON|sudo apt-get install -y python3 python3-pip python3-venv python3-dev"

    "uv|uv - Fast Python package manager|ON|curl -LsSf https://astral.sh/uv/install.sh | sh"

    "node|Node.js via nvm + npm|ON|curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash && export NVM_DIR=\"\$HOME/.nvm\" && [ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\" && nvm install --lts"

    "java|OpenJDK 17 + Maven|OFF|sudo apt-get install -y openjdk-17-jdk maven"

    "docker|Docker CE + Compose plugin|ON|sudo install -m 0755 -d /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg && sudo chmod a+r /etc/apt/keyrings/docker.gpg && echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \$(. /etc/os-release && echo \$VERSION_CODENAME) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && sudo usermod -aG docker \$USER"

    "vscode|Visual Studio Code|ON|curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && echo \"deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null && sudo apt-get update && sudo apt-get install -y code"

    "ollama|Ollama - Local LLM runner|OFF|curl -fsSL https://ollama.com/install.sh | sh"

    "n8n|n8n workflow automation (Docker)|OFF|docker pull n8nio/n8n"

    "rust|Rust via rustup|OFF|curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"

    "go|Go (latest official)|OFF|GO_VERSION=\$(curl -s https://go.dev/VERSION?m=text | head -1) && curl -fsSL \"https://go.dev/dl/\${GO_VERSION}.linux-amd64.tar.gz\" -o /tmp/go.tar.gz && sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf /tmp/go.tar.gz && rm /tmp/go.tar.gz && echo 'export PATH=\$PATH:/usr/local/go/bin' >> \$HOME/.bashrc"

    "neovim|Neovim latest stable|OFF|curl -fsSL https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz -o /tmp/nvim.tar.gz && sudo tar -C /usr/local --strip-components=1 -xzf /tmp/nvim.tar.gz && rm /tmp/nvim.tar.gz"

    "tmux|tmux terminal multiplexer|OFF|sudo apt-get install -y tmux"

    "zsh|Zsh + Oh My Zsh|OFF|sudo apt-get install -y zsh && sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended && chsh -s \$(which zsh)"

    "postgresql|PostgreSQL client + server|OFF|sudo apt-get install -y postgresql postgresql-client"

    "redis|Redis server|OFF|sudo apt-get install -y redis-server"

    "nginx|Nginx web server|OFF|sudo apt-get install -y nginx"

    "ssh-server|OpenSSH server|OFF|sudo apt-get install -y openssh-server && sudo systemctl enable --now ssh"

    "firewall|UFW (deny in, allow SSH)|OFF|sudo apt-get install -y ufw && sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw allow ssh && sudo ufw --force enable"

    "fonts|Dev fonts (FiraCode, JetBrains)|OFF|sudo apt-get install -y fonts-firacode fonts-jetbrains-mono"
)

# =============================================================================
# Engine — no need to edit below this line
# =============================================================================

# Check whiptail
if ! command -v whiptail &>/dev/null; then
    echo "Installing whiptail..."
    sudo apt-get update && sudo apt-get install -y whiptail
fi

# Build whiptail checklist args from TOOLS array
CHECKLIST_ARGS=()
for entry in "${TOOLS[@]}"; do
    IFS='|' read -r key desc default _cmd <<< "$entry"
    CHECKLIST_ARGS+=("$key" "$desc" "$default")
done

ITEM_COUNT=${#TOOLS[@]}
HEIGHT=$((ITEM_COUNT + 10))
[ $HEIGHT -gt 35 ] && HEIGHT=35

# Show selection UI
CHOICES=$(whiptail --title "Debian Developer Setup" \
    --checklist "SPACE = toggle, ENTER = confirm:" "$HEIGHT" 70 "$ITEM_COUNT" \
    "${CHECKLIST_ARGS[@]}" \
    3>&1 1>&2 2>&3) || { echo "Cancelled."; exit 0; }

# Always preview first, then ask to proceed
PREVIEW=true

# Execute
if $PREVIEW; then
    echo ""
    echo "========================================="
    echo " COMMANDS THAT WOULD BE EXECUTED:"
    echo "========================================="
    echo ""
fi

for choice in $CHOICES; do
    key=$(echo "$choice" | tr -d '"')

    # Find matching entry
    for entry in "${TOOLS[@]}"; do
        IFS='|' read -r ekey edesc edefault ecmd <<< "$entry"
        if [ "$ekey" = "$key" ]; then
            if $PREVIEW; then
                echo "--- [$key] $edesc ---"
                echo "$ecmd" | tr '&&' '\n'
                echo ""
            else
                log_info "Installing: $key — $edesc"
                eval "$ecmd" && log_ok "$key installed" || echo -e "${YELLOW}[!] $key had errors${NC}"
            fi
            break
        fi
    done
done

if $PREVIEW; then
    echo "========================================="
    echo ""
    if whiptail --title "Proceed?" \
        --yesno "Install the above tools now?" 8 40; then
        PREVIEW=false
        echo ""
        for choice in $CHOICES; do
            key=$(echo "$choice" | tr -d '"')
            for entry in "${TOOLS[@]}"; do
                IFS='|' read -r ekey edesc edefault ecmd <<< "$entry"
                if [ "$ekey" = "$key" ]; then
                    log_info "Installing: $key — $edesc"
                    eval "$ecmd" && log_ok "$key installed" || echo -e "${YELLOW}[!] $key had errors${NC}"
                    break
                fi
            done
        done
        echo ""
        log_ok "All done! Log out and back in for group changes to take effect."
    else
        echo "Aborted. Nothing was installed."
    fi
else
    echo ""
    log_ok "All done! Log out and back in for group changes to take effect."
fi
