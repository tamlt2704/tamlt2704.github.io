#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Developer Setup Tool for Fresh Debian
# Uses whiptail for interactive selection
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
log_info() { echo -e "${YELLOW}[+]${NC} $1"; }
log_err()  { echo -e "${RED}[✗]${NC} $1"; }

# Check if whiptail is available
if ! command -v whiptail &>/dev/null; then
    echo "Installing whiptail..."
    sudo apt-get update && sudo apt-get install -y whiptail
fi

# =============================================================================
# Selection UI
# =============================================================================

CHOICES=$(whiptail --title "Debian Developer Setup" \
    --checklist "Select tools to install (SPACE to toggle, ENTER to confirm):" 30 70 20 \
    "essentials"    "Build tools, git, curl, wget, htop, tree, jq" ON \
    "python"        "Python 3 + pip + venv" ON \
    "uv"            "uv - Fast Python package manager" ON \
    "node"          "Node.js (via nvm) + npm" ON \
    "java"          "OpenJDK 17 + Maven" OFF \
    "docker"        "Docker CE + Compose plugin" ON \
    "vscode"        "Visual Studio Code" ON \
    "ollama"        "Ollama - Local LLM runner" OFF \
    "n8n"           "n8n - Workflow automation (Docker)" OFF \
    "rust"          "Rust (via rustup)" OFF \
    "go"            "Go (latest from official tarball)" OFF \
    "neovim"        "Neovim (latest stable)" OFF \
    "tmux"          "tmux terminal multiplexer" OFF \
    "zsh"           "Zsh + Oh My Zsh" OFF \
    "postgresql"    "PostgreSQL client + server" OFF \
    "redis"         "Redis server" OFF \
    "nginx"         "Nginx web server" OFF \
    "ssh-server"    "OpenSSH server" OFF \
    "firewall"      "UFW firewall (deny incoming, allow SSH)" OFF \
    "fonts"         "Developer fonts (FiraCode, JetBrains Mono)" OFF \
    3>&1 1>&2 2>&3) || { echo "Cancelled."; exit 0; }

# =============================================================================
# Preview mode - show commands before running
# =============================================================================

if whiptail --title "Preview or Install?" \
    --yesno "Do you want to PREVIEW commands first?\n\n(Yes = show commands only, No = install now)" 10 60; then
    PREVIEW=true
else
    PREVIEW=false
fi

# =============================================================================
# Installation functions
# =============================================================================

install_essentials() {
    local cmd="sudo apt-get update && sudo apt-get install -y \\
    build-essential git curl wget htop tree jq unzip zip \\
    ca-certificates gnupg lsb-release software-properties-common \\
    apt-transport-https net-tools dnsutils"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Essentials installed"; fi
}

install_python() {
    local cmd="sudo apt-get install -y python3 python3-pip python3-venv python3-dev"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Python installed"; fi
}

install_uv() {
    local cmd='curl -LsSf https://astral.sh/uv/install.sh | sh'
    if $PREVIEW; then echo "$cmd"; else
        if command -v uv &>/dev/null; then log_ok "uv already installed"
        else eval "$cmd" && log_ok "uv installed"; fi
    fi
}

install_node() {
    local cmd='curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install --lts'
    if $PREVIEW; then echo "$cmd"; else
        if command -v node &>/dev/null; then log_ok "Node already installed: $(node --version)"
        else eval "$cmd" && log_ok "Node.js installed via nvm"; fi
    fi
}

install_java() {
    local cmd="sudo apt-get install -y openjdk-17-jdk maven"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Java 17 + Maven installed"; fi
}

install_docker() {
    local cmd='sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER'
    if $PREVIEW; then echo "$cmd"; else
        if command -v docker &>/dev/null; then log_ok "Docker already installed"
        else eval "$cmd" && log_ok "Docker installed (re-login for group)"; fi
    fi
}

install_vscode() {
    local cmd='curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
sudo apt-get update
sudo apt-get install -y code'
    if $PREVIEW; then echo "$cmd"; else
        if command -v code &>/dev/null; then log_ok "VS Code already installed"
        else eval "$cmd" && log_ok "VS Code installed"; fi
    fi
}

install_ollama() {
    local cmd='curl -fsSL https://ollama.com/install.sh | sh'
    if $PREVIEW; then echo "$cmd"; else
        if command -v ollama &>/dev/null; then log_ok "Ollama already installed"
        else eval "$cmd" && log_ok "Ollama installed"; fi
    fi
}

install_n8n() {
    local cmd='docker pull n8nio/n8n'
    if $PREVIEW; then echo "$cmd"; else
        if docker image inspect n8nio/n8n &>/dev/null 2>&1; then log_ok "n8n already pulled"
        else eval "$cmd" && log_ok "n8n Docker image pulled"; fi
    fi
}

install_rust() {
    local cmd='curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
    if $PREVIEW; then echo "$cmd"; else
        if command -v rustc &>/dev/null; then log_ok "Rust already installed"
        else eval "$cmd" && log_ok "Rust installed"; fi
    fi
}

install_go() {
    local cmd='GO_VERSION=$(curl -s https://go.dev/VERSION?m=text | head -1)
curl -fsSL "https://go.dev/dl/${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz
echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc'
    if $PREVIEW; then echo "$cmd"; else
        if command -v go &>/dev/null; then log_ok "Go already installed: $(go version)"
        else eval "$cmd" && log_ok "Go installed"; fi
    fi
}

install_neovim() {
    local cmd='curl -fsSL https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz -o /tmp/nvim.tar.gz
sudo tar -C /usr/local --strip-components=1 -xzf /tmp/nvim.tar.gz
rm /tmp/nvim.tar.gz'
    if $PREVIEW; then echo "$cmd"; else
        if command -v nvim &>/dev/null; then log_ok "Neovim already installed"
        else eval "$cmd" && log_ok "Neovim installed"; fi
    fi
}

install_tmux() {
    local cmd="sudo apt-get install -y tmux"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "tmux installed"; fi
}

install_zsh() {
    local cmd='sudo apt-get install -y zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
chsh -s $(which zsh)'
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Zsh + Oh My Zsh installed"; fi
}

install_postgresql() {
    local cmd="sudo apt-get install -y postgresql postgresql-client"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "PostgreSQL installed"; fi
}

install_redis() {
    local cmd="sudo apt-get install -y redis-server"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Redis installed"; fi
}

install_nginx() {
    local cmd="sudo apt-get install -y nginx"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Nginx installed"; fi
}

install_ssh_server() {
    local cmd="sudo apt-get install -y openssh-server && sudo systemctl enable --now ssh"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "SSH server installed and enabled"; fi
}

install_firewall() {
    local cmd="sudo apt-get install -y ufw && sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw allow ssh && sudo ufw --force enable"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "UFW configured"; fi
}

install_fonts() {
    local cmd="sudo apt-get install -y fonts-firacode fonts-jetbrains-mono"
    if $PREVIEW; then echo "$cmd"; else eval "$cmd" && log_ok "Developer fonts installed"; fi
}

# =============================================================================
# Run selected installations
# =============================================================================

if $PREVIEW; then
    echo ""
    echo "========================================="
    echo " COMMANDS THAT WOULD BE EXECUTED:"
    echo "========================================="
    echo ""
fi

for choice in $CHOICES; do
    # Remove quotes from whiptail output
    item=$(echo "$choice" | tr -d '"')
    
    if $PREVIEW; then
        echo "--- [$item] ---"
    else
        log_info "Installing: $item"
    fi

    case "$item" in
        essentials)   install_essentials ;;
        python)       install_python ;;
        uv)           install_uv ;;
        node)         install_node ;;
        java)         install_java ;;
        docker)       install_docker ;;
        vscode)       install_vscode ;;
        ollama)       install_ollama ;;
        n8n)          install_n8n ;;
        rust)         install_rust ;;
        go)           install_go ;;
        neovim)       install_neovim ;;
        tmux)         install_tmux ;;
        zsh)          install_zsh ;;
        postgresql)   install_postgresql ;;
        redis)        install_redis ;;
        nginx)        install_nginx ;;
        ssh-server)   install_ssh_server ;;
        firewall)     install_firewall ;;
        fonts)        install_fonts ;;
    esac

    if $PREVIEW; then echo ""; fi
done

if $PREVIEW; then
    echo "========================================="
    echo " Run again and choose 'No' to install."
    echo "========================================="
else
    echo ""
    log_ok "All done! You may need to log out and back in for some changes to take effect."
fi
